import json

def export_to_json(data, file_name):
    """
    Exports data to a JSON file.

    Args:
        data (dict): The data to export.
        file_name (str): The name of the JSON file to create.
    """
    with open(file_name, 'w') as f:
        json.dump(data, f)

# Example usage
export_to_json({
    "bidders": bidders,
    "sellers": sellers,
    "all_bids": retrieve_all_bids()
}, "auction_data.json")