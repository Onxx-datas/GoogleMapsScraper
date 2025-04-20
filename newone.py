import requests
import pandas as pd
import threading
import time
import os
import random
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

# ===== BLOCK 1: Enhanced API Keys & Proxy Setup =====
API_KEYS = [

]

# Proxy rotation setup (BLOCK 6)
PROXY_LIST = [
    "http://user:pass@gate1:port",
    "http://user:pass@gate2:port",
    "http://user:pass@gate3:port"
]

PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# ===== BLOCK 2: Hyper-Optimized Grid Parameters =====
CENTER_LAT = 52.51475784439185
CENTER_LNG = 13.398880854990345
SHIFT = [x * 0.0012 for x in range(-5, 6)]  # 11x11 grid (121 points)
RADIUS = 1500  # Smaller radius for hyper-local overlaps
MAX_RESULTS = 350

# ===== BLOCK 3: Compound Type Fusion =====
PLACE_TYPES = ['museum|bar', 'restaurant|tourist_attraction', 'hotel|spa']

# ===== BLOCK 4: Parallel Processing Core =====
def parallel_token_harvest(tokens):
    with ThreadPoolExecutor(max_workers=len(API_KEYS)) as executor:
        futures = [executor.submit(fetch_pages, token) for token in tokens]
        return [f.result() for f in futures]

def get_places(api_key, params):
    params['key'] = api_key
    # Proxy rotation implementation (BLOCK 6)
    proxy = {"http": random.choice(PROXY_LIST), "https": random.choice(PROXY_LIST)}
    try:
        response = requests.get(PLACES_URL, params=params, proxies=proxy, timeout=10)
        return response.json()
    except:
        return {'results': [], 'status': 'REQUEST_FAILED'}

def get_places_with_all_pages(api_key, params):
    all_results = []
    while True:
        data = get_places(api_key, params)
        
        # ===== BLOCK 5: Response Decay Handling =====
        if 'error' in data:
            time.sleep(random.uniform(1.8, 3.2))  # Randomized delay
            api_index = (API_KEYS.index(api_key) + 1) % len(API_KEYS)
            api_key = API_KEYS[api_index]
            continue
            
        results = data.get('results', [])
        all_results.extend(results)

        next_token = data.get('next_page_token')
        if not next_token:
            break
        params['pagetoken'] = next_token
        time.sleep(random.uniform(1.8, 2.5))  # Randomized delay

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
                'type': place_type,
                # ===== BLOCK 6: Data Enrichment Fields =====
                'fields': 'current_opening_hours,reviews,website,price_level'
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
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", filename)
    
    data = []
    for place in places:
        place_data = {
            'Name': place.get('name'),
            'Place ID': place.get('place_id'),
            'Types': ', '.join(place.get('types', [])),
            'Address': place.get('vicinity'),
            'Latitude': place.get('geometry', {}).get('location', {}).get('lat'),
            'Longitude': place.get('geometry', {}).get('location', {}).get('lng'),
            # ===== BLOCK 6: Enhanced Data Extraction =====
            'Opening Hours': str(place.get('current_opening_hours', {}).get('weekday_text', [])),
            'Reviews Snapshot': str([r.get('text')[:50] for r in place.get('reviews', [])][:3]),
            'Price Level': place.get('price_level', 'N/A')
        }
        data.append(place_data)

    df = pd.DataFrame(data)
    df.to_excel(desktop_path, index=False, engine='openpyxl')
    print(f"✅ Data saved to {desktop_path}")

if __name__ == "__main__":
    places = get_all_places_grid()
    print(f"\n✅ Done! Total unique places found: {len(places)}")
    save_to_excel(places)