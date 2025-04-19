import requests
import pandas as pd
import time
import os

API_KEYS = [
    "AIzaSyAXjiKHAlaWdEKF_QIdNX7wNmbMjud_1XQ",
    "AIzaSyBcjel-BwPSUrZ4Bw_-Exu1hhIyOneSDuE",
    "AIzaSyAHkvuQ9Y0E6nK-u_Fs98pYXWpyD5ZL_0M"
]

PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

CENTER_LAT = 52.51475784439185
CENTER_LNG = 13.398880854990345
SHIFT = [-0.004, 0, 0.004]
RADIUS = 5000
MAX_RESULTS = 350

PLACE_TYPES = ['museum', 'bar', 'restaurant', 'hotel', 'lodging']

def get_places(api_key, params):
    params['key'] = api_key
    response = requests.get(PLACES_URL, params=params)
    return response.json()

def get_places_with_all_pages(api_key, params):
    all_results = []
    while True:
        data = get_places(api_key, params)
        results = data.get('results', [])
        all_results.extend(results)

        next_token = data.get('next_page_token')
        if not next_token:
            break
        params['pagetoken'] = next_token
        time.sleep(2)
    return all_results

def get_all_places_grid():
    results = []
    place_ids_seen = set()
    api_index = 0

    grid_points = [
        (CENTER_LAT + dy, CENTER_LNG + dx)
        for dy in SHIFT
        for dx in SHIFT
    ]

    for place_type in PLACE_TYPES:
        for lat, lng in grid_points:
            if len(results) >= MAX_RESULTS:
                break

            print(f"\n📍 Searching at {lat}, {lng} for type '{place_type}'")
            params = {
                'location': f'{lat},{lng}',
                'radius': RADIUS,
                'type': place_type
            }

            api_key = API_KEYS[api_index]
            api_index = (api_index + 1) % len(API_KEYS)

            new_places = get_places_with_all_pages(api_key, params)

            for place in new_places:
                pid = place['place_id']
                if pid not in place_ids_seen:
                    results.append(place)
                    place_ids_seen.add(pid)

                if len(results) >= MAX_RESULTS:
                    break

            print(f"✅ Total unique places so far: {len(results)}")

        if len(results) >= MAX_RESULTS:
            break

    return results

def save_to_excel(places, filename="places_results.xlsx"):
    # Explicitly set path to save to desktop
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", filename)
    
    # Extract relevant data
    data = []
    for place in places:
        place_data = {
            'Name': place.get('name'),
            'Place ID': place.get('place_id'),
            'Types': ', '.join(place.get('types', [])),
            'Address': place.get('vicinity'),
            'Latitude': place.get('geometry', {}).get('location', {}).get('lat'),
            'Longitude': place.get('geometry', {}).get('location', {}).get('lng')
        }
        data.append(place_data)

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Save to Excel
    df.to_excel(desktop_path, index=False, engine='openpyxl')
    print(f"✅ Data saved to {desktop_path}")

places = get_all_places_grid()
print(f"\n✅ Done! Total unique places found: {len(places)}")
save_to_excel(places)
