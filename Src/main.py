import copy

from SimEngine import *
import Sellers
from Bid import *
from AuctionRound import *
from Bidders import *
from ReferenceCalculator import *
from Behaviour import *
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
    fair_combination = find_combinations(all_blocks, 2500)
    # Sort combinations by their fairness index, highest first
    most_fair_combination = max(fair_combination, key=lambda x: x[1])[0] if combinations else None

    evaluation = evaluate_combinations(fair_combination, 2500)
    print(f"bidders = {bidders}")
    print(f"Sellers = {sellers}")
    print(f"blocks = {all_blocks}")
    print(f"combinations = {fair_combination}")
    print(f"evalution = {evaluation}")
    print(f"most_fair_combination = {most_fair_combination}")


    # Example: Conduct 5 auction rounds
    conduct_auction(all_blocks, bidders, 5)

    # Retrieve and display all bids after the auction
    all_bids = retrieve_all_bids()
    print("All bids:", all_bids)



    if conf["distance-limit"] != None:
        overrideLimit(bidders, conf["distance-limit"])
    if conf["distance-penalty"] != None:
        overridePenalty(bidders, conf["distance-penalty"])

    noAuctions, sellerList = initSellers(sellers)
    bidderList = initBidders(bidders, math.ceil(noAuctions / conf["slotsize"]))

    print(sellerList)
    print(bidderList)
    #return conf['slotsize'], conf['end-threshold'], sellerList, bidderList
    #return conf['slotsize'], conf['end-threshold'], sellerList
    return conf['slotsize'], conf['end-threshold']


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
            #"price": random.randrange(1, 3) * quantity,
            "price": quantity,
            "discount": discount,
            "seller_id": seller_id,
            "highest_bid": {"amount": 0, "bidder_id": None},  # Placeholder for the highest bid
        }
        block_id = col_blocks.insert_one(block_data)
        blocks["block" + str(j)] = block_data
    return blocks


def genBidders(number, demand, radius, limit, penalty):
    bidders = {}
    dividers = sorted(random.sample(range(1, demand), number))
    demands = [a - b for a, b in zip(dividers + [demand], [0] + dividers)]
    for i in range(number):

        random_behaviour = randomBehaviour()
        behavior = genBehaviour(random_behaviour)
        behavior_attrs = {
            "behavior_type": random_behaviour,
            "aggressiveness": behavior.aggressiveness,
            "marketPriceFactor": behavior.marketPriceFactor,
            "stopBid": behavior.stopBid,
            "bidLikelyhood": behavior.bidLikelyhood,
            # Include other relevant attributes
        }

        bidder_data = {
            "location": genLocation(radius),
            "need": demands.pop(),
            "behavior": behavior_attrs,
            "distanceLimit": limit,
            "distancePenalty": penalty
        }
        # Insert the bidder into the database
        insert_result = col_bidders.insert_one(bidder_data)
        # Update the bidder_data with the MongoDB-generated _id
        bidder_data['_id'] = insert_result.inserted_id
        # Add the updated bidder_data to the bidders dictionary
        bidders[f"Bidder{i}"] = bidder_data
        #bidders_list = copy.deepcopy(bidders[f"Bidder{i}"])
        #x_bidders = col_bidders.insert_one(bidders_list)
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

    #Recursively finds combinations of blocks that meet or exceed the target quantity.
    total_quantity = sum(block["quantity"] for block in current_combination)
    if total_quantity >= target_quantity:
        fairness_index = calculate_jains_fairness_index([block["quantity"] for block in current_combination], target_quantity)
        return [(current_combination, fairness_index)]

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


def calculate_jains_fairness_index(quantities, target_quantity):
    """
    Calculate Jain's Fairness Index for a given combination of quantities
    against the target quantity.

    :param quantities: A list of quantities in the current combination.
    :param target_quantity: The target total quantity desired.
    :return: The Jain's Fairness Index for the combination.
    """
    if not quantities:
        return 0  # Avoid division by zero

    scaled_quantities = [q / target_quantity for q in quantities]
    sum_of_scaled = sum(scaled_quantities)
    sum_of_squares_scaled = sum(q ** 2 for q in scaled_quantities)
    n = len(quantities)
    fairness_index = (sum_of_scaled ** 2) / (n * sum_of_squares_scaled) if n * sum_of_squares_scaled else 0
    return fairness_index


def evaluate_combinations(combinations, target_quantity):

    if not combinations:
        return None

    # Filter out combinations that do not meet the target quantity, if necessary
    # This step might be redundant depending on how find_combinations is implemented
    valid_combinations = [(combo, fairness) for combo, fairness in combinations if
                          sum(block["quantity"] for block in combo) >= target_quantity]

    # Balance between fairness and minimizing excess quantity
    best_combination = min(valid_combinations,
                           key=lambda x: (sum(block["quantity"] for block in x[0]) - target_quantity, -x[1]))

    return best_combination[0] if best_combination else None
# def evaluate_combinations(combinations, target_quantity):
#     # Example: Find combination with least waste
#     best_combination = None
#     least_waste = float('inf')
#     for combination in combinations:
#         total_quantity = sum(block["quantity"] for block in combination)
#         waste = total_quantity - target_quantity
#         if waste < least_waste:
#             best_combination = combination
#             least_waste = waste
#     return best_combination


def place_bid(block_id, bidder_id, bid_amount):
    block = col_blocks.find_one({"_id": block_id})
    if not block or 'highest_bid' in block and bid_amount <= block['highest_bid']['amount']:
        return False, "Bid is not higher than the current highest bid."

    # Update the block with the new highest bid
    col_blocks.update_one({"_id": block_id}, {"$set": {"highest_bid": {"amount": bid_amount, "bidder_id": bidder_id}}})
    return True, "Bid placed successfully."


def conduct_auction_round(blocks, bidders, round_index):
    print(f"Conducting auction round {round_index}...")
    for bidder_key, bidder_info in bidders.items():  # Correctly iterate over the bidders dictionary
        bidder_id = bidder_info['_id']  # Access the MongoDB _id for the bidder

        # Determine the likelihood of placing a bid
        #likelihood = behavior.adaptiveBidLikelyhoood(currentRound, maxRound, bidIndex=0, unfulfilledNeed=1, distance=0.5)  # Adjust parameters as needed

        for block in blocks:
            # Generate a random bid for demonstration purposes
            bid_amount = calculate_bid_amount(block, bidder_info)
            success, message = place_bid(block['_id'], bidder_id, bid_amount)
            if not success:
                print(f"Failed to place bid: {message}")
            else:
                print(f"Bid of {bid_amount} placed on block {block['_id']} by bidder {bidder_id}")


def calculate_bid_amount(block, bidder_info):

    # Simplified example of calculating bid amount based on behavior and block information
    bid_amount = bidder_info["behavior"]["aggressiveness"] * block["price"] * bidder_info["behavior"]["marketPriceFactor"]
    return bid_amount if bid_amount <= block["price"] * bidder_info["behavior"]["stopBid"] else 0


def retrieve_all_bids():
    all_bids = []
    blocks = col_blocks.find({})
    for block in blocks:
        if "highest_bid" in block:
            all_bids.append({
                "block_id": block['_id'],
                "highest_bid": block['highest_bid']['amount'],
                "bidder_id": block['highest_bid']['bidder_id']
            })
    return all_bids

def conduct_auction(blocks, bidders, num_rounds):
    for i in range(num_rounds):
        conduct_auction_round(blocks, bidders, i)
        # Optionally, you can retrieve and display all bids here or after all rounds


def initSellers(sellers):
    sellerList = []
    noAuctions = 0
    for sellerKey in sellers:
        entity = Sellers.Sellers(sellerKey, sellers[sellerKey]["location"])
        firstBlock = sellers[sellerKey]["blocks"].pop("block1")
        entity.quantity.append(firstBlock[0]['quantity'])
        entity.genBlock(
            firstBlock[1]["price"], firstBlock[0]["quantity"], firstBlock[2]["discount"]
        )
        noAuctions += 1
        for block in sellers[sellerKey]["blocks"].items():
            entity.quantity.append(block[1][0]['quantity'])
            entity.addBlock(
                block[1][1]["price"], block[1][0]["quantity"], block[1][2]["discount"]
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
    slotSize, endThreshold = readConfig(skipPrompts)
    fairness = 1

    fairness = 1
    distance = 1
    print(f"Best fairness value: {fairness}")
    print(f"Average distance {distance}")
    if fairness == None:
        print("No valid combinations were found")
    else:
        auctionResults = []

    #return matchmakingResults, auctionResults
    return auctionResults

if __name__ == "__main__":
    start(False)