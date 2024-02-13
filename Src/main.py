import copy

from SimEngine import *
import Sellers
from Bidders import *
from ReferenceCalculator import *
import random
import math
import yaml
import pymongo
from pymongo import MongoClient

uri = "mongodb+srv://admin-test:test@cluster0.rpqlu.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)
db = client["DSM_Sim"]
col_bidders = db["bidders"]
col_sellers = db["sellers"]
col_blocks = db["blocks"]
x_bidders = col_bidders.delete_many({})
x_sellers = col_sellers.delete_many({})
x_blocks = col_blocks.delete_many({})

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

seed = None

# File names for configs hardcoded, could be set with a user input function
configFile = "config.yaml"
sellerFile = "sellers.yaml"
bidderFile = "bidders.yaml"

# Default limits how many blocks each seller can have randomized
MAX_BLOCK = 3
MIN_BLOCK = 2


def readConfig(skipPrompts):
    "Reads any configs which are present, and generates configs if they do not exist or if user wished to generate them"
    generatedConfig = 0
    try:
        with open(configFile, "r") as f:
            conf = yaml.load(f, Loader=yaml.FullLoader)
    except:
        print("Could not find a config file, generating")
        conf = genConfig()
        generatedConfig = 1
    try:
        with open(sellerFile, "r") as f:
            if not skipPrompts: raise
            sellers = yaml.load(f, Loader=yaml.FullLoader)
        conf["sellers"] = len(sellers)
    except:
        sellers = None

    try:
        with open(bidderFile, "r") as f:
            if not skipPrompts: raise
            bidders = yaml.load(f, Loader=yaml.FullLoader)
        conf["bidders"] = len(bidders)
    except:
        bidders = None
    
    if not generatedConfig:
        verifyConfig(conf)
    
    if conf["min-block"] == None:
        conf["min-block"] = MIN_BLOCK

    if conf["max-block"] == None:
        conf["max-block"] = MAX_BLOCK

    supply, demand = getResourceUsage(sellers, bidders)
    if bidders and sellers:
        conf["resource-usage"] = demand / supply
    elif not bidders and not sellers:
        demand = random.randrange(500, 5000)
        supply = round(demand / conf["resource-usage"])
        bidders = genBidders(conf["bidders"], demand, conf["radius"], conf["distance-limit"], conf["distance-penalty"])
        sellers = genSellers(conf["sellers"], supply, conf["radius"], conf)
    elif bidders and not sellers:
        supply = round(demand / conf["resource-usage"])
        sellers = genSellers(conf["sellers"], supply, conf["radius"])
    else:
        demand = round(conf["resource-usage"] * supply)
        bidders = genBidders(conf["bidders"], demand, conf["radius"], conf["distance-limit"], conf["distance-penalty"])

    all_blocks = retrieve_all_blocks()
    combination = find_combinations(all_blocks, 5000)
    print(f"bidders = {bidders}")
    print(f"Sellers = {sellers}")
    print(f"blocks = {all_blocks}")
    print(f"combinations = {combination}")
    
    if conf["distance-limit"] != None:
        overrideLimit(bidders, conf["distance-limit"])
    if conf["distance-penalty"] != None:
        overridePenalty(bidders, conf["distance-penalty"])

    noAuctions, sellerList = initSellers(sellers)
    bidderList = initBidders(bidders, math.ceil(noAuctions / conf["slotsize"]))
    return conf['slotsize'], conf['end-threshold'], sellerList, bidderList


def genConfig():
    """Generates a config.yaml file and saves it"""
    conf = {}
    conf["seed"] = random.randrange(0, 10000)
    random.seed(conf["seed"])
    conf["sellers"] = random.randrange(5, 15)
    conf["bidders"] = random.randrange(2, 7)
    conf["resource-usage"] = round(random.uniform(0.25, 0.9), 4)
    conf["radius"] = random.randint(2, 10)
    conf["distance-limit"] = round(random.uniform(conf["radius"]*1.5, conf["radius"]*3),2)
    conf["distance-penalty"] = round(random.uniform(5,10),2)
    conf["slotsize"] = 2
    conf["end-threshold"] = 2
    with open("config.yaml", "w") as f:
        yaml.dump(conf, f, sort_keys=False)


def verifyConfig(conf):
    if not conf["seed"]:
        conf["seed"] = random.randrange(0, 10000)
    random.seed(conf["seed"])
    if not conf["sellers"]:
        conf["sellers"] = random.randrange(5, 15)
    if not conf["bidders"]:
        conf["bidders"] = random.randrange(2, 7)
    if not conf["resource-usage"]:
        conf["resource-usage"] = round(random.uniform(0.25, 0.9), 4)
    if not conf["radius"]:
        conf["radius"] = random.randint(2,10)
    if not conf["distance-limit"]:
        conf["distance-limit"] = round(random.uniform(conf["radius"]*1.5, conf["radius"]*3),2)
    if not conf["distance-penalty"]:    
        conf["distance-penalty"] = round(random.uniform(5,10),2)
    if not conf["slotsize"]:
        conf["slotsize"] = 2
    if not conf["end-threshold"]:
        conf["end-threshold"] = 2


def genSellers(number, supply, radius, conf):
    sellers = {}
    dividers = sorted(random.sample(range(1, supply), number-1))
    supplies = [a - b for a, b in zip(dividers + [supply], [0] + dividers)]
    for i in range(number):
        toDistribute = supplies.pop()
        chainLen = random.randint(conf['min-block'], conf['max-block'])
        div = sorted(random.sample(range(1, toDistribute), chainLen))
        values = [a - b for a, b in zip(div + [toDistribute], [0] + div)]
        # Insert placeholder seller to get the seller_id
        seller_placeholder = {
            "location": genLocation(radius),
        }
        inserted_id = col_sellers.insert_one(seller_placeholder).inserted_id
        # Generate blocks with the actual seller_id
        blocks = genBlocks(values, inserted_id)
        # Update the seller document with the generated blocks
        col_sellers.update_one({"_id": inserted_id}, {"$set": {"blocks": blocks}})
        sellers[f"Seller{i}"] = {
            "location": seller_placeholder["location"],
            "blocks": blocks,
        }
    return sellers


def genBlocks(values, seller_id):
    blocks = {}
    for j in range(len(values)):
        discount = 0
        quantity = values[j]
        if j != 0:
            discount = round(random.uniform(0.1, 0.50), 2)
        # si se cambia de lista a objecto es decir de [] a {} mejora la data en mongodb
        block_data = {
            "quantity": quantity,
            "price": random.randrange(1, 3) * quantity,
            "discount": discount,
            "seller_id": seller_id,
        }
        block_id = col_blocks.insert_one(block_data)
        blocks["block" + str(j)] = block_data
    return blocks


def genBidders(number, demand, radius, limit, penalty):
    bidders = {}
    dividers = sorted(random.sample(range(1, demand), number))
    demands = [a - b for a, b in zip(dividers + [demand], [0] + dividers)]
    for i in range(number):
        bidders["Bidder" + str(i)] = {
            "location": genLocation(radius),
            "need": demands.pop(),
            "behavior": Behaviour.randomBehaviour(),
            "distanceLimit": limit,
            "distancePenalty": penalty
        }
        bidders_list = copy.deepcopy(bidders[f"Bidder{i}"])
        x_bidders = col_bidders.insert_one(bidders_list)
    return bidders


def retrieve_all_blocks():
    all_blocks = []
    sellers = col_sellers.find({})
    for seller in sellers:
        if "blocks" in seller:
            for block_id, block in seller["blocks"].items():
                all_blocks.append(block)
                all_blocks[-1]["seller_id"] = seller["_id"]  # Add seller_id to block for reference
    return all_blocks

def getResourceUsage(sellers, bidders):
    supply = 0
    if sellers:
        for sellerKey in sellers:
            for block in sellers[sellerKey]["blocks"].items():
                supply += block[1][0]["quantity"]
    demand = 0
    if bidders:
        for bidderKey in bidders:
            demand += bidders[bidderKey]["need"]
    return supply, demand


def find_combinations(blocks, target_quantity, current_combination=[], start=0):
    """
    Recursively finds combinations of blocks that meet or exceed the target quantity.
    """
    total_quantity = sum(block["quantity"] for block in current_combination)
    if total_quantity >= target_quantity:
        return [current_combination]

    if start >= len(blocks):
        return []

    combinations = []
    # Include current block
    include_current = find_combinations(blocks, target_quantity, current_combination + [blocks[start]], start + 1)
    # Exclude current block
    exclude_current = find_combinations(blocks, target_quantity, current_combination, start + 1)

    combinations.extend(include_current)
    combinations.extend(exclude_current)

    return combinations

def evaluate_combinations(combinations):
    # Example: Find combination with least waste
    best_combination = None
    least_waste = float('inf')
    for combination in combinations:
        total_quantity = sum(block["quantity"] for block in combination)
        waste = total_quantity - target_quantity
        if waste < least_waste:
            best_combination = combination
            least_waste = waste
    return best_combination

def initSellers(sellers):
    sellerList = []
    noAuctions = 0
    for sellerKey in sellers:
        entity = Sellers.Sellers(sellerKey, sellers[sellerKey]["location"])
        firstBlock = sellers[sellerKey]["blocks"].pop("block1")
        entity.quantity.append(firstBlock['quantity'])
        entity.genBlock(
            firstBlock["price"], firstBlock["quantity"], firstBlock["discount"]
        )
        noAuctions += 1
        for block in sellers[sellerKey]["blocks"].items():
            entity.quantity.append(block[1]['quantity'])
            entity.addBlock(
                block[1]["price"], block[1]["quantity"], block[1]["discount"]
            )
            noAuctions += 1
        sellerList.append(entity)
    return noAuctions, sellerList


def initBidders(bidders, maxRounds):
    bidderList = []
    for bidder in bidders.items():
        data = bidder[1]
        entity = Bidders(
            bidder[0],
            data["location"],
            data["need"],
            maxRounds,
            Behaviour.genBehaviour(data["behavior"]),
            data["distanceLimit"],
            data["distancePenalty"]
        )
        bidderList.append(entity)
    return bidderList

# Source with explanation: https://stackoverflow.com/a/50746409
def genLocation(radius):
    "Generate x,y points within circle with set radius with center in 0,0"
    r = radius * math.sqrt(random.random())
    theta = random.random() * 2 * math.pi
    x = round(r * math.cos(theta), 4)
    y = round(r * math.sin(theta), 4)
    return [x, y]

def overrideLimit(bidders, limit):
    for bidder in bidders.items():
        bidder[1]['distanceLimit'] = limit

def overridePenalty(bidders, penalty):
    for bidder in bidders.items():
        bidder[1]['distancePenalty'] = penalty

def start(skipPrompts):
    slotSize, endThreshold, sellerList, bidderList = readConfig(skipPrompts)
    fairness = 1
    #TODO Serialize matchmaking results and store in appropriate way
    #matchmakingResults = matchMakingCalculation(sellerList, bidderList)
    #fairness = matchmakingResults[0].get('fairness', None)
    #distance = matchmakingResults[0].get('avgDistance', None)
    fairness = 1
    distance = 1
    print(f"Best fairness value: {fairness}")
    print(f"Average distance {distance}")
    if fairness == None:
        print("No valid combinations were found")
    if skipPrompts:
        #mp = matchmakingResults[0]['avgPrice']
        mp = 12
        for bidder in bidderList:               # Give bidders a marketprice (price per unit) in order to formulate bids
            bidder.setMarketprice(mp)
        engine = SimEngine(sellerList, bidderList, slotSize, endThreshold)
        auctionResults = engine.simStart()
    else:
        auctionResults = []

    #return matchmakingResults, auctionResults
    return auctionResults

if __name__ == "__main__":
    start(False)