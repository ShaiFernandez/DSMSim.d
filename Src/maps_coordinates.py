import requests


def get_coordinates_from_address(address, google_maps_api_key):
    """
    Use the Google Maps Geocoding API to get the latitude and longitude of a given address.

    :param address: The address to geocode.
    :param google_maps_api_key: Your Google Maps API key.
    :return: A tuple containing the latitude and longitude of the address.
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": google_maps_api_key}
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            # Extract latitude and longitude
            latitude = data["results"][0]["geometry"]["location"]["lat"]
            longitude = data["results"][0]["geometry"]["location"]["lng"]
            return latitude, longitude
        else:
            return None, None  # Address not found or API limit exceeded
    else:
        return None, None  # Request failed


# Example usage
google_maps_api_key = "YOUR_API_KEY_HERE"
address = "1600 Amphitheatre Parkway, Mountain View, CA"
latitude, longitude = get_coordinates_from_address(address, google_maps_api_key)
print(f"Coordinates: Latitude = {latitude}, Longitude = {longitude}")