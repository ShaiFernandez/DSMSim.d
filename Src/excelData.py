import pandas as pd

def export_to_excel(data, file_name):
    """
    Exports data to an Excel file.

    Args:
        data (dict): A dictionary where each key is a sheet name and each value is a pandas DataFrame.
        file_name (str): The name of the Excel file to create.
    """
    with pd.ExcelWriter(file_name) as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

# Example usage
bidders_df = pd.DataFrame(bidders)  # Assuming `bidders` is a dictionary or a list of dictionaries
sellers_df = pd.DataFrame(sellers)  # Same assumption as above
all_bids_df = pd.DataFrame(retrieve_all_bids())

data = {
    "Bidders": bidders_df,
    "Sellers": sellers_df,
    "Bids": all_bids_df
}

export_to_excel(data, "auction_data.xlsx")