import pandas as pd
from bson import ObjectId  # If using ObjectId, make sure to import it for handling


def export_data_to_excel(bidders, sellers, evaluations, all_bids, bid_evaluation, all_bids_by_block, bid_evaluation_by_block, list_prints, list_prints_blocks):
    # Flattening the data
    rows = []
    for bidder, info in bidders.items():
        row = {
            'Bidder': bidder,
            'Bidder ID': str(info['_id']),  # Convert ObjectId to string
            'City': info['location']['city'],
            'State': info['location']['state'],
            'Latitude': info['location']['latitude'],
            'Longitude': info['location']['longitude'],
            'Need': info['need'],
            'Behavior Type': info['behavior']['behavior_type'],
            'Aggressiveness Init': info['behavior_init']['aggressiveness'],
            'Market Price Factor Init': info['behavior_init']['marketPriceFactor'],
            'Stop Bid Init': info['behavior_init']['stopBid'],
            'Bid Likelihood Init': info['behavior_init']['bidLikelihood'],
            'Aggressiveness': info['behavior']['aggressiveness'],
            'Market Price Factor': info['behavior']['marketPriceFactor'],
            'Stop Bid': info['behavior']['stopBid'],
            'Bid Likelihood': info['behavior']['bidLikelihood'],
            #'Distance Limit': info['distanceLimit'],
            #'Distance Penalty': info['distancePenalty'],
            #'Fulfilled Need': info['fulfilled_need'],

        }
        rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Flattening the data
    seller_rows = []
    for seller, info in sellers.items():
        for block_name, block_details in info['blocks'].items():
            row = {
                'Seller': seller,
                'Seller ID': str(info['_id']),
                'City': info['location']['city'],
                'State': info['location']['state'],
                'Latitude': info['location']['latitude'],
                'Longitude': info['location']['longitude'],
                'Block Name': block_name,
                'Block ID': str(block_details['_id']),
                'Quantity': block_details['quantity'],
                'Price': block_details['price'],
                #'Highest Bid Amount': block_details['highest_bid']['amount'],
                #'Highest Bidder ID': block_details['highest_bid']['bidder_id'],
                #'Round Last Bid': block_details['round_last_bid'],
            }
            seller_rows.append(row)

    # Create DataFrame for sellers
    df_sellers = pd.DataFrame(seller_rows)

    # Flatten the evaluations data
    evaluation_rows = []
    for evaluation_group in evaluations:
        for evaluation in evaluation_group:
            row = {
                'Bidder ID': evaluation['bidder_id'],
                'Quantity': evaluation['target_quantity'],
                'Total Quantity': evaluation['total_quantity'],
                #'Price': evaluation['price'],
                'Sellers ID': evaluation['sellers_id'],
                #'Seller ID': str(evaluation['seller_id']),
                'Blocks ID': evaluation['blocks_id'],
                #'Block ID': str(evaluation['_id']),
                'Discount %': evaluation['discount_percentage'],
                'Discount': evaluation['discount'],
                'Waste': evaluation['waste'],
                'Waste Additional Cost %': evaluation['additional_cost_percentage'],
                'Average Distance Km': evaluation['avg_distance'],
                'Truck Emissions': evaluation['truck_emissions'],
                'Plane Emissions': evaluation['plane_emissions'],
                'Recommended Mode': evaluation['recommended_mode'],
                'CO2 Additional Cost %': evaluation['co2_additional_cost'],
                'Normalized Environmental Impact': evaluation['normalized_environmental_impact'],
                'Price Total Blocks': evaluation['total_price'],
                'Price Bid Discount': evaluation['total_price_discount'],
                'Price Bid Waste': evaluation['total_price_waste'],
                'Price Bid Co2': evaluation['total_price_co2'],
                'Price Total': evaluation['total_price_tax'],
                'Fairness Index': evaluation['fairness_index'],
                'Fairness Percentage': evaluation['fairness_percentage'],
                'Normalized Fairness': evaluation['normalized_fairness'],
                'Weight Waste-Co2': evaluation['weight_waste_co2'],
                'Weight Fairness': evaluation['weight_fairness'],
                'Score': evaluation['score']
            }
            evaluation_rows.append(row)

    # Create DataFrame for evaluations
    df_evaluations = pd.DataFrame(evaluation_rows)

    # Flatten the bids data
    bid_rows = []
    for bid in all_bids:
        row = {
            'Block ID': str(bid['block_id']),
            'Highest Bid': bid['highest_bid'],
            'Bidder ID': str(bid['bidder_id'])
        }
        bid_rows.append(row)

    # Create DataFrame for bids
    df_bids = pd.DataFrame(bid_rows)


    # Flatten the bids data
    prints_rows = []
    for printer in list_prints:
        row = {
            'Auction by round': printer,
        }
        prints_rows.append(row)

    # Create DataFrame for bids
    df_prints_round = pd.DataFrame(prints_rows)


    # Flatten the evaluations data
    bid_evaluation_rows = []
    for evaluation_bid in bid_evaluation:

        row = {
            'Bidder ID': str(evaluation_bid['bidder_id']),
            'Quantity': evaluation_bid['target_quantity'],
            'Total Quantity': evaluation_bid['total_quantity'],
            #'Price': evaluation_bid['price'],
            'Sellers ID': evaluation_bid['sellers_id'],
            'Blocks ID': evaluation_bid['blocks_id'],
            'Discount %': evaluation_bid['discount_percentage'],
            'Discount': evaluation_bid['discount'],
            'Waste': evaluation_bid['waste'],
            'Waste Additional Cost %': evaluation_bid['additional_cost_percentage'],
            'Average Distance Km': evaluation_bid['avg_distance'],
            'Truck Emissions': evaluation_bid['truck_emissions'],
            'Plane Emissions': evaluation_bid['plane_emissions'],
            'Recommended Mode': evaluation_bid['recommended_mode'],
            'CO2 Additional Cost %': evaluation_bid['co2_additional_cost'],
            'Normalized Environmental Impact': evaluation_bid['normalized_environmental_impact'],
            'Price Total Blocks': evaluation_bid['total_price'],
            'Price Total Bid': evaluation_bid['total_price_bid'],
            'Price Bid Discount': evaluation_bid['total_price_bid_discount'],
            'Price Bid Waste': evaluation_bid['total_price_bid_waste'],
            'Price Bid Co2': evaluation_bid['total_price_bid_co2'],
            'Price Total': evaluation_bid['total_price_bid_tax'],
            'Fairness Index': evaluation_bid['fairness_index'],
            'Fairness Percentage': evaluation_bid['fairness_percentage'],
            'Normalized Fairness': evaluation_bid['normalized_fairness'],
            'Weight Waste-Co2': evaluation_bid['weight_waste_co2'],
            'Weight Fairness': evaluation_bid['weight_fairness'],
            'Score': evaluation_bid['score']
        }
        bid_evaluation_rows.append(row)
    #
     # Create DataFrame for evaluations
    df_bid_evaluations = pd.DataFrame(bid_evaluation_rows)


    # Flatten the bids data
    bid_rows_by_block = []
    for bid in all_bids_by_block:
        row = {
            'Block ID': str(bid['block_id']),
            'Highest Bid': bid['highest_bid'],
            'Bidder ID': str(bid['bidder_id'])
        }
        bid_rows_by_block.append(row)

    # Create DataFrame for bids
    df_bids_by_block = pd.DataFrame(bid_rows_by_block)


    # Flatten the bids data
    prints_blocks_rows = []
    for printer in list_prints_blocks:
        row = {
            'Auction by round': printer,
        }
        prints_blocks_rows.append(row)

    # Create DataFrame for bids
    df_prints_blocks = pd.DataFrame(prints_blocks_rows)



    # Flatten the evaluations data
    bid_evaluation_rows_by_block = []
    for evaluation_bid in bid_evaluation_by_block:

        row = {
            'Bidder ID': str(evaluation_bid['bidder_id']),
            'Quantity': evaluation_bid['target_quantity'],
            'Total Quantity': evaluation_bid['total_quantity'],
            #'Price': evaluation_bid['price'],
            'Sellers ID': evaluation_bid['sellers_id'],
            'Blocks ID': evaluation_bid['blocks_id'],
            'Discount %': evaluation_bid['discount_percentage'],
            'Discount': evaluation_bid['discount'],
            'Waste': evaluation_bid['waste'],
            'Waste Additional Cost %': evaluation_bid['additional_cost_percentage'],
            'Average Distance Km': evaluation_bid['avg_distance'],
            'Truck Emissions': evaluation_bid['truck_emissions'],
            'Plane Emissions': evaluation_bid['plane_emissions'],
            'Recommended Mode': evaluation_bid['recommended_mode'],
            'CO2 Additional Cost %': evaluation_bid['co2_additional_cost'],
            'Normalized Environmental Impact': evaluation_bid['normalized_environmental_impact'],
            'Price Total Blocks': evaluation_bid['total_price'],
            'Price Total Bid': evaluation_bid['total_price_bid'],
            'Price Bid Discount': evaluation_bid['total_price_bid_discount'],
            'Price Bid Waste': evaluation_bid['total_price_bid_waste'],
            'Price Bid Co2': evaluation_bid['total_price_bid_co2'],
            'Price Total': evaluation_bid['total_price_bid_tax'],
            'Fairness Index': evaluation_bid['fairness_index'],
            'Fairness Percentage': evaluation_bid['fairness_percentage'],
            'Normalized Fairness': evaluation_bid['normalized_fairness'],
            'Weight Waste-Co2': evaluation_bid['weight_waste_co2'],
            'Weight Fairness': evaluation_bid['weight_fairness'],
            'Score': evaluation_bid['score']
        }
        bid_evaluation_rows_by_block.append(row)
    #
     # Create DataFrame for evaluations
    df_bid_evaluations_by_block = pd.DataFrame(bid_evaluation_rows_by_block)


    # Save to Excel
    with pd.ExcelWriter('combined_data.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Bidders', index=False)  # Assuming df is your DataFrame from the bidders
        df_sellers.to_excel(writer, sheet_name='Sellers', index=False)
        df_evaluations.to_excel(writer, sheet_name='evaluation_results.xlsx', index=False)
        #df_bids.to_excel(writer, sheet_name='bid_results.xlsx', index=False)
        #df_prints_round.to_excel(writer, sheet_name='auction_results_round.xlsx', index=False)
        #df_bid_evaluations.to_excel(writer, sheet_name='bids_evaluation_results.xlsx', index=False)
        df_bids_by_block.to_excel(writer, sheet_name='bid_by_block.xlsx', index=False)
        df_prints_blocks.to_excel(writer, sheet_name='auction_results_block.xlsx', index=False)
        df_bid_evaluations_by_block.to_excel(writer, sheet_name='bids_evaluation_by_block.xlsx', index=False)