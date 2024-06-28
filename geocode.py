from mapbox import Geocoder
import os

def geocode_address(address):
    # Retrieve the Mapbox access token from an environment variable inside the function
    access_token = os.getenv('MAPBOX_ACCESS_TOKEN')
    if not access_token:
        raise ValueError("Mapbox access token is not set in environment variables.")

    geocoder = Geocoder(access_token=access_token)
    response = geocoder.forward(address)
    
    # Check if the response is successful
    if response.status_code == 200:
        # Parse the JSON response
        json_data = response.json()
        
        # Extract latitude and longitude
        coordinates = json_data['features'][0]['geometry']['coordinates']
        return {'lat': coordinates[1], 'lng': coordinates[0]}
    else:
        return None

