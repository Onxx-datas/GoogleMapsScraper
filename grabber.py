# import requests
# import pandas as pd
# import time
# import os
# import random
# from concurrent.futures import ThreadPoolExecutor



# API_KEYS = [

# ]



# PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"



# CENTER_LAT = 52.51475784439185
# CENTER_LNG = 13.398880854990345
# SHIFT = [x * 0.0012 for x in range(-5, 6)]
# RADIUS = 1500
# MAX_RESULTS = 350



# PLACE_TYPES = ['museum|bar', 'restaurant|tourist_attraction', 'hotel|spa']



# def get_places(api_key, params):
#     params['key'] = api_key
#     try:
#         response = requests.get(PLACES_URL, params=params, timeout=10)
#         return response.json()
#     except Exception as e:
#         print(f"Request failed: {e}")
#         return {'results': [], 'status': 'REQUEST_FAILED'}



# def fetch_page(args):
#     api_key, params = args
#     return get_places(api_key, params)



# def parallel_token_harvest(token_params):
#     with ThreadPoolExecutor(max_workers=len(API_KEYS)) as executor:
#         results = list(executor.map(fetch_page, token_params))
#     return results



# def get_places_with_all_pages(api_key, params):
#     all_results = []
#     while True:
#         data = get_places(api_key, params)
#         if 'error' in data:
#             time.sleep(random.uniform(1.8, 3.2))
#             continue
#         results = data.get('results', [])
#         all_results.extend(results)
#         next_token = data.get('next_page_token')
#         if not next_token:
#             break
#         params['pagetoken'] = next_token
#         time.sleep(random.uniform(1.8, 2.5))
#     return all_results



# def get_all_places_grid():
#     results = []
#     place_ids_seen = set()
#     api_index = 0
#     grid_points = [
#         (CENTER_LAT + dy, CENTER_LNG + dx)
#         for dy in SHIFT
#         for dx in SHIFT
#     ]
#     for place_type in PLACE_TYPES:
#         for lat, lng in grid_points:
#             if len(results) >= MAX_RESULTS:
#                 break
#             print(f"\n📍 Searching at {lat}, {lng} for type '{place_type}'")
#             params = {
#                 'location': f'{lat},{lng}',
#                 'radius': RADIUS,
#                 'type': place_type,
#                 'fields': 'current_opening_hours,reviews,website,price_level'
#             }
#             api_key = API_KEYS[api_index]
#             api_index = (api_index + 1) % len(API_KEYS)
#             new_places = get_places_with_all_pages(api_key, params)
#             for place in new_places:
#                 pid = place['place_id']
#                 if pid not in place_ids_seen:
#                     results.append(place)
#                     place_ids_seen.add(pid)
#                 if len(results) >= MAX_RESULTS:
#                     break
#             print(f"✅ Total unique places so far: {len(results)}")
#         if len(results) >= MAX_RESULTS:
#             break
#     return results
    


# def save_to_excel(places, filename="places_results.xlsx"):
#     desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", filename)
#     data = []
#     for place in places:
#         place_data = {
#             'Name': place.get('name'),
#             'Place ID': place.get('place_id'),
#             'Types': ', '.join(place.get('types', [])),
#             'Address': place.get('vicinity'),
#             'Latitude': place.get('geometry', {}).get('location', {}).get('lat'),
#             'Longitude': place.get('geometry', {}).get('location', {}).get('lng'),
#             'Opening Hours': str(place.get('current_opening_hours', {}).get('weekday_text', [])),
#             'Price Level': place.get('price_level', 'N/A')
#         }
#         data.append(place_data)
#     df = pd.DataFrame(data)
#     df.to_excel(desktop_path, index=False, engine='openpyxl')
#     print(f"✅ Data saved to {desktop_path}")



# if __name__ == "__main__":
#     places = get_all_places_grid()
#     print(f"\n✅ Done! Total unique places found: {len(places)}")
#     save_to_excel(places)