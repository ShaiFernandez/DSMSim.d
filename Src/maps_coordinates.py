import random
import math
import json

def load_locations(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Load the seed file
seed_locations = load_locations('locations.json')

def genLocation(locations, radius):
    """
    Generate a random location within a specified radius around a central point from a list of locations.

    Args:
    - locations (list): A list of locations loaded from the seed file.
    - radius (float): The radius around the center point within which to generate a location, in meters.

    Returns:
    - A dictionary with the selected city's details and the generated latitude and longitude.
    """
    # Select a random city from the list
    city = random.choice(locations)

    # Convert radius from meters to degrees (approximation)
    radius_in_degrees = radius / 111000  # Rough approximation

    # Generate random angle
    angle = random.uniform(0, 2 * math.pi)

    # Calculate delta latitude and longitude
    delta_lat = radius_in_degrees * math.cos(angle)
    delta_lon = radius_in_degrees * math.sin(angle) / math.cos(math.radians(city['latitude']))

    # Generate new coordinates
    new_lat = city['latitude'] + delta_lat
    new_lon = city['longitude'] + delta_lon

    # Add the new coordinates to the city's details
    city['generated_latitude'] = new_lat
    city['generated_longitude'] = new_lon

    return city


# Example usage
radius = 1000  # Radius in meters
generated_location = genLocation(seed_locations, radius)
print(generated_location)