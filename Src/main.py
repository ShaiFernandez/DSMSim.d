import copy

from SimEngine import *
import Sellers
from Bid import *
from AuctionRound import *
from Bidders import *
from ReferenceCalculator import *
from excelData import *
from Cities import *
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

    if conf["min-block"] is None:
        conf["min-block"] = MIN_BLOCK

    if conf["max-block"] is None:
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

    #  evaluate logic
    list_evaluations = []
    list_prints = []
    list_prints_block = []
    all_blocks = retrieve_all_blocks()
    for bidder_key, bidder_info in bidders.items():
        bidder = bidders[bidder_key]
        target_quantity = bidder_info["need"]
        combinations = find_combinations(all_blocks, target_quantity)
        evaluation = evaluate_combinations(combinations, target_quantity, bidder, sellers)
        list_evaluations.append(evaluation)

        # Now, you can do something with each bidder's fair combination.
        #most_fair_combination = max(combinations, key=lambda x: x[1])[0] if combinations else None

        # For example, printing, storing, or further processing.
        print(f"Bidder {bidder_key}'s combinations: ", combinations)
        #print(f"most_fair_combination = {most_fair_combination}")
        print(f"evaluation = {evaluation}")

        # You could extend this to evaluate, store, or use these combinations in auction logic

    # fair_combination = find_combinations(all_blocks, 2500)
    # Sort combinations by their fairness index, highest first

    # evaluation = evaluate_combinations(fair_combination, 2500)

    print(f"bidders = {bidders}")
    print(f"Sellers = {sellers}")
    print(f"blocks = {all_blocks}")
    print(f"evaluations = {list_evaluations}")
    # print(f"combinations = {fair_combination}")

    # Example: Conduct 5 auction rounds
    conduct_auction(all_blocks, bidders, 10, list_prints)
    all_bids = retrieve_all_bids()
    print("All bids:", all_bids)
    # Retrieve and display all bids after the auction
    bid_evaluation = evaluate_winning_bids(all_bids)
    print("bid_evaluations:", bid_evaluation)

    #blocks_highest_bid_change = col_blocks.find()
    for block in all_blocks:
        block_id = block['_id']
        new_highest_bid = {"$set": {"highest_bid": {"amount": 0, "bidder_id": None}}}

        # Update the bidder_data with the MongoDB-generated _id
        col_blocks.update_one({"_id": block_id}, new_highest_bid)

    conduct_auction_by_block(all_blocks, bidders, 10, list_prints_block)
    all_bids_by_block = retrieve_all_bids()
    print("All bids by block:", all_bids_by_block)
    bid_evaluation_by_block = evaluate_winning_bids(all_bids_by_block)
    print("bid_evaluations:", bid_evaluation_by_block)




    if conf["distance-limit"] != None:
        overrideLimit(bidders, conf["distance-limit"])
    if conf["distance-penalty"] != None:
        overridePenalty(bidders, conf["distance-penalty"])

    return bidders, sellers, list_evaluations, all_bids, bid_evaluation, all_bids_by_block, bid_evaluation_by_block, list_prints, list_prints_block


def genConfig():
    """Generates a config.yaml file and saves it"""
    conf = {}
    conf["seed"] = random.randrange(0, 10000)
    random.seed(conf["seed"])
    conf["sellers"] = random.randrange(5, 15)
    conf["bidders"] = random.randrange(2, 7)
    conf["resource-usage"] = round(random.uniform(0.25, 0.9), 4)
    conf["radius"] = random.randint(2, 10)
    conf["distance-limit"] = round(random.uniform(conf["radius"] * 1.5, conf["radius"] * 3), 2)
    conf["distance-penalty"] = round(random.uniform(5, 10), 2)
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
        conf["radius"] = random.randint(2, 10)
    if not conf["distance-limit"]:
        conf["distance-limit"] = round(random.uniform(conf["radius"] * 1.5, conf["radius"] * 3), 2)
    if not conf["distance-penalty"]:
        conf["distance-penalty"] = round(random.uniform(5, 10), 2)
    if not conf["slotsize"]:
        conf["slotsize"] = 2
    if not conf["end-threshold"]:
        conf["end-threshold"] = 2


def genSellers(number, supply, radius, conf):
    sellers = {}
    dividers = sorted(random.sample(range(1, supply), number - 1))
    supplies = [a - b for a, b in zip(dividers + [supply], [0] + dividers)]
    for i in range(number):
        toDistribute = supplies.pop()
        chainLen = random.randint(conf['min-block'], conf['max-block'])
        div = sorted(random.sample(range(1, toDistribute), chainLen-1))
        values = [a - b for a, b in zip(div + [toDistribute], [0] + div)]
        # Insert placeholder seller to get the seller_id
        seller_placeholder = {
            "location": selectRandomCity(),
        }
        seller_id = col_sellers.insert_one(seller_placeholder).inserted_id
        # Generate blocks with the actual seller_id
        blocks = genBlocks(values, seller_id)
        # Update the seller document with the generated blocks
        col_sellers.update_one({"_id": seller_id}, {"$set": {"blocks": blocks}})
        sellers[f"Seller{i}"] = {
            "_id": seller_id,
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
            #"discount": discount,
            "seller_id": seller_id,
            "highest_bid": {"amount": 0, "bidder_id": None},  # Placeholder for the highest bid
            "round_last_bid": 0  # Initialize the round_last_bid attribute to 0
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
        behavior = genBehaviour(random_behaviour, "none", "none", "none", "none")
        behavior_attrs = {
            "behavior_type": random_behaviour,
            "aggressiveness": behavior.aggressiveness,
            "marketPriceFactor": behavior.marketPriceFactor,
            "stopBid": behavior.stopBid,
            "bidLikelihood": behavior.bidLikelihood,
             #Include other relevant attributes
        }

        bidder_data = {
            #"location": genLocation(radius),
            "location": selectRandomCity(),
            "need": demands.pop(),
            "behavior_init": behavior_attrs,
            "behavior": behavior_attrs,
            "distanceLimit": limit,
            "distancePenalty": penalty,
            "fulfilled_need": 0  # Initialize fulfilled_need attribute
        }
        # Insert the bidder into the database
        insert_result = col_bidders.insert_one(bidder_data)
        # Update the bidder_data with the MongoDB-generated _id
        bidder_data['_id'] = insert_result.inserted_id
        # Add the updated bidder_data to the bidders dictionary
        bidders[f"Bidder{i}"] = bidder_data
        # bidders_list = copy.deepcopy(bidders[f"Bidder{i}"])
        # x_bidders = col_bidders.insert_one(bidders_list)
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
    # Recursively finds combinations of blocks that meet or exceed the target quantity.
    total_quantity = sum(block["quantity"] for block in current_combination)
    if total_quantity >= target_quantity:
        #fairness_index = calculate_jains_fairness_index([block["quantity"] for block in current_combination], target_quantity)
        #return [(current_combination, fairness_index)]

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


def calculate_total_price(transactions, carbon_price, cost_per_km, waste_cost_per_unit):
    total_prices = []

    for transaction in transactions:
        # Assuming 'transaction' contains quantity of waste, distance traveled, CO2 emissions, etc.
        distance_cost = transaction['distance'] * cost_per_km
        co2_cost = transaction['co2'] * carbon_price
        waste_cost = transaction['waste'] * waste_cost_per_unit

        # Price behavior could include adjustments based on demand, urgency, etc.
        # Market price is the base price of the service or product.
        adjusted_price = transaction['market_price'] * transaction['price_behavior']

        # Apply discounts
        final_price = adjusted_price + distance_cost + co2_cost + waste_cost - transaction['discount']

        total_prices.append(final_price)

    return total_prices



def evaluate_combinations(combinations, target_quantity, bidder, sellers):
    best_combination = None
    least_waste = float('inf')
    best_fairness = 0
    best_avg_distance = float('inf')

    augmented_combinations = []

    #for combination, fairness_index in combinations:
    for combination in combinations:

        # Calculate the total discount for the combination
        discount, total_cost_before_discount, discount_percentage = calculate_discount_for_combination(combination, sellers)
        total_cost_after_discount = total_cost_before_discount - discount


        #sellers = {block['seller_id']: retrieve_seller_info(block['seller_id']) for block in blocks}
        sellers_id=[]
        sellers_id.append([str(block['seller_id']) for block in combination])
        blocks_id = []
        blocks_id.append([str(block['_id']) for block in combination])

        total_quantity = sum(block["quantity"] for block in combination)
        waste = total_quantity - target_quantity

        additional_cost_percentage = calculate_waste_taxation(waste, target_quantity)
        print(f"Additional cost due to waste: {additional_cost_percentage}%")

        # Assuming you have a way to calculate the average distance for this combination
        avg_distance = calculate_average_distance(combination, bidder, sellers)

        # Example distance
        emissions_info = calculate_co2_emissions(avg_distance)

        print(f"Average Distance: {emissions_info['avg_distance']} km")
        print(f"Truck Emissions: {emissions_info['truck_emissions']} kg of CO2")
        print(f"Plane Emissions: {emissions_info['plane_emissions']} kg of CO2")
        print(f"Recommended Transportation Mode: {emissions_info['recommended_mode']}")

        additional_cost_due_to_co2 = calculate_co2_taxation(emissions_info)
        print(f"Additional cost due to CO2 emissions: {additional_cost_due_to_co2}%")

        total_price = sum(block["price"] for block in combination)
        price_discount = total_price - discount
        price_tax_waste = total_price * ((100 + additional_cost_percentage)/100)
        price_tax_co2 = total_price * ((100 + additional_cost_due_to_co2)/100)
        final_price = (total_price - discount) * ((100 + additional_cost_percentage)/100) * ((100 + additional_cost_due_to_co2)/100)

        fairness_percentage = calculate_fairness_percentage(total_price, final_price)
        fairness_list = [price_discount, price_tax_waste, price_tax_co2, final_price]
        #fairness_index = calculate_jains_fairness_index([block["quantity"] for block in combination], target_quantity)
        fairness_index = calculate_jains_fairness_index(fairness_list, total_price)
        print(f"fairness index: {fairness_index}")


        norm_env_impact = invert_normalize(additional_cost_due_to_co2 + additional_cost_percentage, 60)
        norm_fairness = normalize(invert_normalize(fairness_percentage, 1) + fairness_index, 2)
        print(f"Normalize value: {norm_env_impact}")

        weight_waste_co2 = 0.5  # 50% importance
        weight_fairness = 0.5  # 50% importance

        score = calculate_score(norm_env_impact, norm_fairness, weight_waste_co2, weight_fairness)
        print(f"total score value: {score}")

        # Augment the combination data
        augmented_data = {
            'bidder_id': bidder['_id'],
            'target_quantity': target_quantity,
            'total_quantity': total_quantity,
            'sellers_id': sellers_id,
            'blocks_id': blocks_id,
            'discount_percentage': discount_percentage,
            'discount': discount,
            'waste': waste,
            'additional_cost_percentage': additional_cost_percentage,
            'avg_distance': avg_distance,
            'truck_emissions': emissions_info['truck_emissions'],
            'plane_emissions': emissions_info['plane_emissions'],
            'recommended_mode': emissions_info['recommended_mode'],
            'co2_additional_cost': additional_cost_due_to_co2,
            'total_price': total_price,
            'total_price_discount': price_discount,
            'total_price_waste': price_tax_waste,
            'total_price_co2': price_tax_co2,
            'total_price_tax': final_price,
            'fairness_index': fairness_index,
            'fairness_percentage': fairness_percentage,
            'normalized_fairness': norm_fairness,
            'normalized_environmental_impact': norm_env_impact,
            'weight_waste_co2': weight_waste_co2,
            'weight_fairness': weight_fairness,
            'score': score
        }
        augmented_combination = {**combination[0], **augmented_data}  # Assuming combination is a list of dicts
        augmented_combinations.append(augmented_combination)

        # Return the list of augmented combinations
    return augmented_combinations


def calculate_score(normalized_waste_co2, normalized_fairness, weight_waste_co2, weight_fairness):
    """Calculate a weighted environmental score based on waste and CO2 metrics."""
    total_score = (normalized_waste_co2 * weight_waste_co2) + (normalized_fairness * weight_fairness)
    return total_score


def invert_normalize(value, max_value):
    """Invert normalize a value based on the maximum possible value."""
    if max_value == 0:
        return 1  # Avoid division by zero; if max_value is 0, value should also be 0, resulting in the best score.
    return 1 - (value / max_value)


def normalize(value, max_value):
    """Invert normalize a value based on the maximum possible value."""
    if max_value == 0:
        return 0  # Avoid division by zero; if max_value is 0, value should also be 0, resulting in the best score.
    return value / max_value


def normalize(value, max_value):
    """Normalize a value to a 0-1 scale based on a provided maximum value."""
    return value / max_value if max_value else 0


def evaluate_combinations_weight(combinations, bidders, sellers):
    best_score = float('-inf')
    best_combination = None
    weight_fairness = 0.7  # Adjust these weights based on your preference
    weight_distance = 0.3

    for combination, fairness_index in combinations:
        avg_distance = calculate_average_distance(combination, bidders, sellers)
        score = weight_fairness * fairness_index - weight_distance * avg_distance
        if score > best_score:
            best_score = score
            best_combination = combination

    return best_combination


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

    #scaled_quantities = [q / target_quantity for q in quantities]
    #sum_of_scaled = sum(scaled_quantities)
    #sum_of_squares_scaled = sum(q ** 2 for q in scaled_quantities)
    #n = len(quantities)
    #fairness_index = (sum_of_scaled ** 2) / (n * sum_of_squares_scaled) if n * sum_of_squares_scaled else 0
    #return fairness_index

    #fairness_index_ind = []
    #for q in quantities:
    #    sum_scaled = (q + target_quantity) ** 2
    #    sum_scaled_div = 2 * (q ** 2 + target_quantity ** 2)
    #    fairness_index_ind.append(sum_scaled / sum_scaled_div)
    #fairness_index = sum(fairness_index_ind) / len(fairness_index_ind)

    scaled_quantities = [q - target_quantity for q in quantities]
    min_value = min(scaled_quantities)
    if min_value < 0:
        scaled_quantities_min = [q + abs(min_value) for q in scaled_quantities]
        sum_of_scaled = sum(scaled_quantities_min)
        sum_of_squares_scaled = sum(q ** 2 for q in scaled_quantities_min)
    else:
        sum_of_scaled = sum(scaled_quantities)
        sum_of_squares_scaled = sum(q ** 2 for q in scaled_quantities)
    n = len(quantities)
    fairness_index = (sum_of_scaled ** 2) / (n * sum_of_squares_scaled) if n * sum_of_squares_scaled else 0

    return fairness_index


def calculate_fairness_percentage(demanded_price, final_price):
    """
    Calculate Fairness Percentage

    """
    if final_price <= 0:
        return 0  # Avoid division by zero


    f_percentage = ((final_price * 100 ) / demanded_price) - 100

    # Apply taxation based on waste percentage
    if f_percentage < 5:
        return 0  # No additional cost for waste below 5%
    elif 5 <= f_percentage < 10:
        return 0.1  # Moderate increase for waste between % and %
    elif 10 <= f_percentage < 15:
        return 0.2  # Higher increase for waste above %
    elif 15 <= f_percentage < 20:
        return 0.3  # Higher increase for waste above %
    elif 20 <= f_percentage < 25:
        return 0.4  # Higher increase for waste above %
    elif 25 <= f_percentage < 30:
        return 0.5  # Higher increase for waste above %
    elif 30 <= f_percentage < 35:
        return 0.6  # Higher increase for waste above %
    elif 35 <= f_percentage < 40:
        return 0.7  # Higher increase for waste above %
    elif 40 <= f_percentage < 45:
        return 0.8  # Higher increase for waste above %
    elif 45 <= f_percentage < 50:
        return 0.9  # Higher increase for waste above %
    else:
        return 1  # Higher increase for waste above %


def calculate_discount_for_combination(combination, sellers):
    """
    Calculate the total discount for a combination based on multiple blocks purchased from the same seller.

    Args:
    - combination: A list of blocks, where each block is a dictionary containing 'seller_id' and 'price'.
    - sellers: A dictionary of sellers, for additional seller info if needed.

    Returns:
    - Total discount for the combination.
    - Total price before discount.
    """
    # Initialize a dictionary to count blocks per seller
    blocks_per_seller = {}
    # Initialize total cost before discount
    total_cost_before_discount = 0

    # Count blocks per seller and calculate total cost
    for block in combination:
        seller_id = block['seller_id']
        blocks_per_seller[seller_id] = blocks_per_seller.get(seller_id, 0) + 1
        total_cost_before_discount += block['price']

    # Initialize total discount
    total_discount = 0
    discount_percentage = 0
    # Calculate discount based on blocks per seller
    for seller_id, count in blocks_per_seller.items():
        if count > 1:  # More than one block from the same seller
            discount_percentage = get_discount_percentage(count)
            # Calculate discount for blocks from this seller
            seller_blocks_total = sum(block['price'] for block in combination if block['seller_id'] == seller_id)
            total_discount += seller_blocks_total * (discount_percentage / 100)

    return total_discount, total_cost_before_discount, discount_percentage

def get_discount_percentage(number_of_blocks):
    """
    Returns the discount percentage based on the number of blocks purchased from the same seller.
    """
    if number_of_blocks == 2:
        return 5  # 5% discount for 2 blocks
    elif number_of_blocks == 3:
        return 7.5  # 7.5% discount for 3 blocks
    elif number_of_blocks > 3:
        return 10  # 10% discount for 4 or more blocks
    return 0  # No discount for 1 block


def calculate_waste_taxation(waste, total_product_volume):
    """
    Calculate additional cost based on waste percentage.

    Args:
    - waste: The amount of waste generated.
    - total_product_volume: The total volume of product purchased.

    Returns:
    - The additional cost or taxation due to waste.
    """
    # Calculate the waste percentage
    #total_volume = waste + total_product_volume
    total_volume = total_product_volume
    if total_volume <= 0:
        return 0  # Avoid division by zero

    waste_percentage = (waste / total_volume) * 100

    # Apply taxation based on waste percentage
    if waste_percentage < 5:
        return 0  # No additional cost for waste below 5%
    elif 5 <= waste_percentage < 10:
        return 2  # Moderate increase for waste between % and %
    elif 10 <= waste_percentage < 20:
        return 4  # Higher increase for waste above %
    elif 20 <= waste_percentage < 50:
        return 6  # Higher increase for waste above %
    elif 50 <= waste_percentage < 100:
        return 10  # Higher increase for waste above %
    elif 100 <= waste_percentage < 150:
        return 15  # Higher increase for waste above %
    elif 150 <= waste_percentage < 300:
        return 20  # Higher increase for waste above %
    else:
        return 30  # Higher increase for waste above %


def calculate_co2_taxation(emissions_info):
    """
    Calculate additional cost based on CO2 emissions.

    Args:
    - co2_emissions: The amount of CO2 emissions in kilograms.

    Returns:
    - The additional cost or taxation due to CO2 emissions.
    """
    # Define CO2 emission thresholds (in kg) and corresponding tax rates (as a percentage of cost)
    # Calculate the CO2 emission percentage
    co2_emissions = 0
    base_co2_emissions = 100
    recommended_mode = emissions_info['recommended_mode']

    if recommended_mode == "truck":
        co2_emissions = emissions_info['truck_emissions']
    else:
        co2_emissions = emissions_info['plane_emissions']


    if co2_emissions <= 0:
        return 0  # Avoid division by zero

    #co2_emissions_percentage = co2_emissions - base_co2_emissions

    # Apply taxation based on waste percentage
    if (co2_emissions < 150 and recommended_mode == "truck") or (co2_emissions < 400 and recommended_mode != "truck"):
        return 0  # No additional cost for waste below 5%
    elif (co2_emissions < 250 and recommended_mode == "truck") or (co2_emissions < 700 and recommended_mode != "truck"):
        return 2  # Moderate increase for waste between 5% and 10%
    elif (co2_emissions < 400 and recommended_mode == "truck") or (co2_emissions < 1000 and recommended_mode != "truck"):
        return 4  # Moderate increase for waste between 5% and 10%
    elif (co2_emissions < 600 and recommended_mode == "truck") or (co2_emissions < 1500 and recommended_mode != "truck"):
        return 6  # Moderate increase for waste between 5% and 10%
    elif (co2_emissions < 800 and recommended_mode == "truck") or (co2_emissions < 2000 and recommended_mode != "truck"):
        return 10  # Moderate increase for waste between 5% and 10%
    elif (co2_emissions < 1000 and recommended_mode == "truck") or (co2_emissions < 2750 and recommended_mode != "truck"):
        return 15  # Moderate increase for waste between 5% and 10%
    elif (co2_emissions < 1250 and recommended_mode == "truck") or (co2_emissions < 3500 and recommended_mode != "truck"):
        return 20  # Moderate increase for waste between 5% and 10%
    else:
        return 30  # Higher increase for waste above 10%



def calculate_average_distance(combination, bidder, sellers):
    total_distance = 0
    count = 0
    bidder_location = bidder["location"]

    print(f"Bidder Location: {bidder_location}")  # Debug print

    # Create a temporary mapping of ObjectId to seller key (e.g., "Seller0")
    id_to_seller_key = {seller_info["_id"]: key for key, seller_info in sellers.items()}

    for block in combination:
        seller_id = block["seller_id"]
        #if seller_id in sellers:
        if seller_id in id_to_seller_key:
            seller_key = id_to_seller_key[seller_id]
            seller_location = sellers[seller_key]["location"]
            print(f"Seller Location for ID {seller_id}: {seller_location}")  # Debug print
            distance = calculate_distance(bidder_location, seller_location)
            print(f"Calculated Distance: {distance}")  # Debug print
            total_distance += distance
            count += 1
        if block["seller_id"] not in id_to_seller_key:
            print(f"Missing seller for ID: {block['seller_id']}")

    avg_distance = total_distance / count if count > 0 else 0
    print(f"avg_distance: {avg_distance}")
    return avg_distance


def haversine(lat1, lon1, lat2, lon2):
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of Earth in kilometers. Use 3956 for miles
    return c * r


def calculate_distance(bidder_location, seller_location):
    return haversine(bidder_location['latitude'], bidder_location['longitude'],
                     seller_location['latitude'], seller_location['longitude'])


def calculate_co2_emissions(avg_distance, plane_threshold=1500):
    """
    Calculate CO2 emissions based on the average distance, choosing the transportation mode
    based on whether the distance is over a certain threshold.

    Args:
        avg_distance (float): The average distance traveled in kilometers.
        plane_threshold (int): The distance threshold to decide between plane and truck transportation.

    Returns:
        A dictionary with CO2 emissions for both transportation modes and a recommendation.
    """
    # Emission factors in grams of CO2 per kilometer (or per tonne-kilometer for planes)
    truck_emission_factor = 275  # Average for delivery trucks
    plane_emission_factor = 750  # Average for cargo planes per tonne-kilometer

    # Calculate emissions for both modes
    truck_emissions = avg_distance * truck_emission_factor / 1000  # Convert to kg
    plane_emissions = avg_distance * plane_emission_factor / 1000  # Convert to kg

    # Determine recommended mode based on distance and emissions
    recommended_mode = "truck" if avg_distance < plane_threshold else "plane"

    # Return both calculations and a recommendation
    return {
        "truck_emissions": truck_emissions,
        "plane_emissions": plane_emissions,
        "recommended_mode": recommended_mode,
        "avg_distance": avg_distance
    }


def place_bid(block_id, bidder_id, bid_amount):
    block = col_blocks.find_one({"_id": block_id})
    if not block or 'highest_bid' in block and bid_amount <= block['highest_bid']['amount']:
        return False, "Bid is not higher than the current highest bid."

    # Update the block with the new highest bid
    col_blocks.update_one({"_id": block_id}, {"$set": {"highest_bid": {"amount": bid_amount, "bidder_id": bidder_id}}})
    return True, "Bid placed successfully."


def conduct_auction(blocks, bidders, num_rounds, list_prints):
    bids_placed = True  # Flag to track if any bids were placed in any round
    for i in range(num_rounds):
        if bids_placed:
            message_print = f"Conducting auction round {i + 1}..."
            list_prints.append(message_print)
            print(f"Conducting auction round {i + 1}...")
        else:
            message_print = f"No bids placed in round {i + 1}. Ending auction rounds."
            list_prints.append(message_print)
            print(f"No bids placed in round {i + 1}. Ending auction rounds.")
            break

        bids_placed = conduct_auction_round(blocks, bidders, i + 1, num_rounds, list_prints)
        # Optionally, you can retrieve and display all bids here or after all rounds


def conduct_auction_round(blocks, bidders, current_round, total_rounds, list_prints):
    #print(f"Conducting auction round {current_round}...")
    bids_placed = False  # Flag to track if any bids were placed in this round
    for bidder_key, bidder_info in bidders.items():
        bidder_id = bidder_info['_id']
        unfulfilled_need = bidder_info['need'] - bidder_info['fulfilled_need']  # Calculate unfulfilled need

        # Retrieve the behavior instance based on the behavior type stored in bidder_info
        behavior_type = bidder_info['behavior']['behavior_type']
        aggressiveness = bidder_info['behavior']['aggressiveness']
        marketPriceFactor = bidder_info['behavior']['marketPriceFactor']
        stopBid = bidder_info['behavior']['stopBid']
        bidLikelihood = bidder_info['behavior']['bidLikelihood']
        bidder_behavior = genBehaviour(behavior_type, aggressiveness, marketPriceFactor, stopBid, bidLikelihood)

        #new_bidder_behavior = {"$set": {"behavior": bidder_behavior.asdict()}}

        # Update the bidder_data with the MongoDB-generated _id
        #col_bidders.update_one({"_id": bidder_id}, new_bidder_behavior)

        # Adjust behavior based on the current round, maximum round, and unfulfilled need
        #bidder_behavior.updateVariables(current_round, total_rounds, unfulfilled_need)

        # Add the updated bidder_data to the bidders dictionary
        bidders[bidder_key]['behavior'] = bidder_behavior.asdict()

        # Determine the likelihood of placing a bid based on adjusted behavior
        bid_likelihood = bidder_behavior.bidLikelihood

        # Check if the bidder will place a bid based on bid likelihood
        if random.random() < bid_likelihood:
            for block in blocks:

                # Adjust behavior based on the current round, maximum round, and difference need
                difference = block["quantity"] - bidder_info["need"]
                bidder_behavior.updateVariablesRound(current_round, total_rounds, difference)

                # Generate a random bid for demonstration purposes
                bid_amount = calculate_bid_amount(block, bidder_info)
                success, message = place_bid(block['_id'], bidder_id, bid_amount)
                if not success:
                    message_print = f"Failed to place bid: {message}"
                    list_prints.append(message_print)
                    print(f"Failed to place bid: {message}")
                else:
                    message_print = f"Bid of {bid_amount} placed on block {block['_id']} by bidder {bidder_id}"
                    list_prints.append(message_print)
                    print(f"Bid of {bid_amount} placed on block {block['_id']} by bidder {bidder_id}")
                    bids_placed = True  # Set the flag to indicate that a bid was placed
        else:
            message_print = f"Failed to place bid {bidder_id} in round {current_round}: not bid based on likelihood"
            list_prints.append(message_print)
            print(f"Failed to place bid {bidder_id} in round {current_round}: not bid based on likelihood")

    return bids_placed

def end_auction(block):
    # Add logic to handle actions when an auction ends
    print(f"Auction for block {block['_id']} has ended.")
    # You can perform actions like logging the outcome, notifying relevant parties, etc.

def calculate_bid_amount(block, bidder_info):
    # Simplified example of calculating bid amount based on behavior and block information
    bid_amount = bidder_info["behavior"]["aggressiveness"] * block["price"] * bidder_info["behavior"][
        "marketPriceFactor"]
    return bid_amount if bid_amount <= block["price"] * bidder_info["behavior"]["stopBid"] else 0


def conduct_auction_by_block(blocks, bidders, num_rounds, list_prints_block):
    for block in blocks:
        message_print = f"Starting auction rounds for block {block['_id']}..."
        list_prints_block.append(message_print)
        print(f"Starting auction rounds for block {block['_id']}...")
        for i in range(num_rounds):
            message_print = f"Conducting round {i + 1} for block {block['_id']}..."
            list_prints_block.append(message_print)
            print(f"Conducting round {i + 1} for block {block['_id']}...")
            # Call a modified auction round function that deals with a single block
            conduct_single_block_round(block, bidders, i + 1, num_rounds, list_prints_block)
        change = col_blocks.find_one({'_id': block['_id']})
        for bidder_key, bidder_info in bidders.items():
            bidder_id = bidder_info['_id']
            bidder_id_change = change['highest_bid']['bidder_id']
            if bidder_id == bidder_id_change:
                bidders[bidder_key]['fulfilled_need'] += change['quantity']


def conduct_single_block_round(block, bidders, current_round, total_rounds, list_prints_block):
    # This function conducts a single round for a single block
    bids_placed = False  # Flag to check if any bids were placed

    for bidder_key, bidder_info in bidders.items():
        bidder_id = bidder_info['_id']
        unfulfilled_need = bidder_info['need'] - bidder_info['fulfilled_need']

        # Retrieve the behavior instance based on the behavior type stored in bidder_info
        behavior_type = bidder_info['behavior']['behavior_type']
        if current_round == 1:
            aggressiveness = bidder_info['behavior_init']['aggressiveness']
            marketPriceFactor = bidder_info['behavior_init']['marketPriceFactor']
            stopBid = bidder_info['behavior_init']['stopBid']
            bidLikelihood = bidder_info['behavior_init']['bidLikelihood']
        else:
            aggressiveness = bidder_info['behavior']['aggressiveness']
            marketPriceFactor = bidder_info['behavior']['marketPriceFactor']
            stopBid = bidder_info['behavior']['stopBid']
            bidLikelihood = bidder_info['behavior']['bidLikelihood']
        bidder_behavior = genBehaviour(behavior_type, aggressiveness, marketPriceFactor, stopBid, bidLikelihood)
        #new_bidder_behavior = {"$set": {"behavior": bidder_behavior.asdict()}}

        # Update the bidder_data with the MongoDB-generated _id
        #col_bidders.update_one({"_id": bidder_id}, new_bidder_behavior)

        # Adjust behavior based on the current round, maximum round, and unfulfilled need
        bidder_behavior.updateVariables(current_round, total_rounds, unfulfilled_need)

        # Add the updated bidder_data to the bidders dictionary
        bidders[bidder_key]['behavior'] = bidder_behavior.asdict()

        # Determine the likelihood of placing a bid based on adjusted behavior
        bid_likelihood = bidder_behavior.bidLikelihood

        # Check if the bidder will place a bid based on bid likelihood
        if random.random() < bid_likelihood and unfulfilled_need > 0:

            # Simulate bidding behavior based on the bidder's attributes and the block's details
            bid_amount = calculate_bid_amount(block, bidder_info)  # Assumes this function exists
            success, message = place_bid(block['_id'], bidder_id, bid_amount)
            if not success:
                message_print = f"Failed to place bid for block {block['_id']} in round {current_round}: {message}"
                list_prints_block.append(message_print)
                print(f"Failed to place bid for block {block['_id']} in round {current_round}: {message}")
            else:
                message_print = f"Bid of {bid_amount} placed on block {block['_id']} by bidder {bidder_id}"
                list_prints_block.append(message_print)
                print(f"Bid of {bid_amount} placed on block {block['_id']} by bidder {bidder_id}")
                bids_placed = True
        else:
            message_print = f"Failed to place bid for block {block['_id']} in round {current_round}: not bid based on likelihood"
            list_prints_block.append(message_print)
            print(f"Failed to place bid for block {block['_id']} in round {current_round}: not bid based on likelihood")

    if not bids_placed:
        message_print = f"No bids placed for block {block['_id']} in round {current_round}."
        list_prints_block.append(message_print)
        print(f"No bids placed for block {block['_id']} in round {current_round}.")


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


def calculate_bidder_fairness(bidder_id, seller_price):
    # Retrieve all bids for the bidder
    all_bids = retrieve_all_bids()
    bidder_bids = [bid['highest_bid'] for bid in all_bids if bid['bidder_id'] == bidder_id]

    if not bidder_bids:
        # If the bidder hasn't placed any bids, return a high fairness score
        return float('inf')

    # Find the highest bid placed by the bidder
    highest_bid = max(bidder_bids)

    # Calculate bidder fairness score based on the difference between bidder's highest bid and seller's price
    bidder_fairness_score = abs(highest_bid - seller_price)

    return bidder_fairness_score

def selectRandomCity():
    return random.choice(cities)


def overrideLimit(bidders, limit):
    for bidder in bidders.items():
        bidder[1]['distanceLimit'] = limit


def overridePenalty(bidders, penalty):
    for bidder in bidders.items():
        bidder[1]['distancePenalty'] = penalty


def evaluate_winning_bids(all_bids):
    # Retrieve all winning bids organized by bidder
    winning_bids_by_bidder = retrieve_winning_blocks_by_bidder(all_bids)

    # Dictionary to hold the evaluations
    evaluations = {}
    bid_evaluation = []
    # Iterate over each bidder's winning blocks
    for bidder_id, blocks in winning_bids_by_bidder.items():
        if not blocks:
            continue
        if bidder_id is None:
            continue

        # Retrieve seller information for discounts calculation
        sellers = {block['seller_id']: retrieve_seller_info(block['seller_id']) for block in blocks}
        sellers_id = [str(block['seller_id']) for block in blocks]
        blocks_id = [str(block['_id']) for block in blocks]

        # Retrieve bidder information for discounts calculation
        bidder = col_bidders.find_one({"_id": bidder_id})
        target_quantity = bidder["need"]

        # Calculate the total discount for the combination
        discount, total_cost_before_discount, discount_percentage = calculate_discount_for_combination(blocks, sellers)
        total_cost_after_discount = total_cost_before_discount - discount

        # Calculate the total quantity won by the bidder
        total_quantity = sum(block["quantity"] for block in blocks)
        waste = total_quantity - target_quantity

        additional_cost_percentage = calculate_waste_taxation(waste, target_quantity)
        print(f"Additional cost due to waste: {additional_cost_percentage}%")

        # Assuming you have a way to calculate the average distance for this combination
        avg_distance = calculate_average_distance(blocks, bidder, sellers)

        # Example distance
        emissions_info = calculate_co2_emissions(avg_distance)

        print(f"Average Distance: {emissions_info['avg_distance']} km")
        print(f"Truck Emissions: {emissions_info['truck_emissions']} kg of CO2")
        print(f"Plane Emissions: {emissions_info['plane_emissions']} kg of CO2")
        print(f"Recommended Transportation Mode: {emissions_info['recommended_mode']}")

        additional_cost_due_to_co2 = calculate_co2_taxation(emissions_info)
        print(f"Additional cost due to CO2 emissions: {additional_cost_due_to_co2}%")

        total_price = sum(block["price"] for block in blocks)
        total_price_bid = sum(block['highest_bid']['amount'] for block in blocks)
        price_tax_waste = total_price_bid * ((100 + additional_cost_percentage) / 100)
        price_tax_co2 = total_price_bid * ((100 + additional_cost_due_to_co2) / 100)
        final_price = (total_price_bid - discount) * ((100 + additional_cost_percentage) / 100) * (
                                     (100 + additional_cost_due_to_co2) / 100)

        fairness_percentage = calculate_fairness_percentage(total_price, final_price)
        fairness_list = [total_price_bid, price_tax_waste, price_tax_co2, final_price]
        # fairness_index = calculate_jains_fairness_index([block["quantity"] for block in combination], target_quantity)
        fairness_index = calculate_jains_fairness_index(fairness_list, total_price)
        print(f"fairness index: {fairness_index}")

        norm_env_impact = invert_normalize(additional_cost_due_to_co2 + additional_cost_percentage, 60)
        norm_fairness = normalize(invert_normalize(fairness_percentage, 1) + fairness_index, 2)
        print(f"Normalize value: {norm_env_impact}")

        weight_waste_co2 = 0.5  # 50% importance
        weight_fairness = 0.5  # 50% importance

        score = calculate_score(norm_env_impact, norm_fairness, weight_waste_co2, weight_fairness)
        print(f"total score value: {score}")

        evaluation_data = {
            'bidder_id': bidder_id,
            'sellers_id': sellers_id,
            'blocks_id': blocks_id,
            'target_quantity': target_quantity,
            'total_quantity': total_quantity,
            'discount_percentage': discount_percentage,
            'discount': discount,
            'waste': waste,
            'additional_cost_percentage': additional_cost_percentage,
            'avg_distance': avg_distance,
            'truck_emissions': emissions_info['truck_emissions'],
            'plane_emissions': emissions_info['plane_emissions'],
            'recommended_mode': emissions_info['recommended_mode'],
            'co2_additional_cost': additional_cost_due_to_co2,
            'total_price': total_price,
            'total_price_bid': total_price_bid,
            'total_price_bid_discount': total_price_bid - discount,
            'total_price_bid_waste':  price_tax_waste,
            'total_price_bid_co2': price_tax_co2,
            'total_price_bid_tax': final_price,
            'fairness_index': fairness_index,
            'fairness_percentage': fairness_percentage,
            'normalized_fairness': norm_fairness,
            'normalized_environmental_impact': norm_env_impact,
            'weight_waste_co2': weight_waste_co2,
            'weight_fairness': weight_fairness,
            'score': score
        }

        bid_evaluation.append(evaluation_data)

        # Return the list of augmented combinations
    return bid_evaluation
    #return score


def retrieve_winning_blocks_by_bidder(all_bids):
    # This function should return a dictionary where the keys are bidder IDs and the values are lists of blocks that the bidder won
    # Placeholder implementation
    winning_blocks = {}
    for bid in all_bids:
        bidder_id = bid['bidder_id']
        block_id = bid['block_id']
        block_details = col_blocks.find_one({"_id": block_id})
        if bidder_id not in winning_blocks:
            winning_blocks[bidder_id] = []
        winning_blocks[bidder_id].append(block_details)
    return winning_blocks


def retrieve_seller_info(seller_id):
    # Function to fetch seller data from database or cache
    return col_sellers.find_one({"_id": seller_id})


def start(skipPrompts):
    bidders, sellers, evaluations, all_bids, bid_evaluation, all_bids_by_block, bid_evaluation_by_block, list_prints, list_prints_blocks = readConfig(skipPrompts)
    fairness = 1
    # TODO Serialize matchmaking results and store in appropriate way
    # matchmakingResults = matchMakingCalculation(sellerList, bidderList)
    # fairness = matchmakingResults[0].get('fairness', None)
    # distance = matchmakingResults[0].get('avgDistance', None)
    export_data_to_excel(bidders, sellers, evaluations, all_bids, bid_evaluation, all_bids_by_block, bid_evaluation_by_block, list_prints, list_prints_blocks)
    fairness = 1
    #print(f"Best fairness value: {fairness}")

    if fairness == None:
        print("No valid combinations were found")
        # if skipPrompts:
        # mp = matchmakingResults[0]['avgPrice']
        mp = 12
        # for bidder in bidderList:               # Give bidders a marketprice (price per unit) in order to formulate bids
        #    bidder.setMarketprice(mp)
        # engine = SimEngine(sellerList, bidderList, slotSize, endThreshold)
        # auctionResults = engine.simStart()
    else:
        auctionResults = []

    # return matchmakingResults, auctionResults
    return auctionResults


if __name__ == "__main__":
    start(False)
