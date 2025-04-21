import requests
import pandas as pd
import time
import random
import os
from geopy.distance import great_circle
from shapely.geometry import Point, shape
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtCore import QObject, pyqtSignal

class CityScraper(QObject):
    update_progress = pyqtSignal(int, str)
    finished = pyqtSignal(pd.DataFrame)
    error_occurred = pyqtSignal(str)

    def __init__(self, city_name, place_type):
        super().__init__()
        self.city_name = city_name
        self.place_type = place_type
        self.running = True

        self.API_KEYS = [   "AIzaSyAXjiKHAlaWdEKF_QIdNX7wNmbMjud_1XQ",
                            "AIzaSyBcjel-BwPSUrZ4Bw_-Exu1hhIyOneSDuE",
                            "AIzaSyAHkvuQ9Y0E6nK-u_Fs98pYXWpyD5ZL_0M"]
        self.SEARCH_SPACING = 500
        self.MAX_RESULTS = 1000

    def get_city_polygon(self):
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={self.city_name}&format=geojson&polygon_geojson=1"
            headers = {
                'User-Agent': 'CityScraperPro/1.0 (contact@yourdomain.com)',
                'Referer': 'https://yourdomain.com'
            }
            
            for attempt in range(3):
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 403:
                    time.sleep(5 ** attempt)
                    continue
                    
                response.raise_for_status()
                data = response.json()
                
                for feature in data['features']:
                    if feature['geometry']['type'] == 'Polygon':
                        return shape(feature['geometry'])
                        
            raise ValueError(f"No polygon found after 3 attempts")
            
        except Exception as e:
            self.error_occurred.emit(
                f"OSM API Error: {str(e)}\n"
                "Required fixes:\n"
                "1. Use 'City, Country' format (e.g., 'Norwich, UK')\n"
                "2. Don't make rapid repeated requests\n"
                "3. Contact admin@openstreetmap.org if blocked"
            )
            return None

    def generate_search_points(self, polygon):
        min_lon, min_lat, max_lon, max_lat = polygon.bounds
        points = []
        
        delta = 0.0045
        lon = min_lon
        while lon <= max_lon:
            lat = min_lat
            while lat <= max_lat:
                if polygon.contains(Point(lon, lat)):
                    points.append((lat, lon))
                lat += delta
            lon += delta
        
        self.update_progress.emit(10, f"📍 Generated {len(points)} search points")
        return points

    def get_places_batch(self, args):
        api_key, params = args
        if not self.running:
            return []
            
        try:
            response = requests.get(
                "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
                params={**params, 'key': api_key},
                timeout=10
            )
            return response.json().get('results', [])
        except Exception as e:
            self.error_occurred.emit(f"API request failed: {str(e)}")
            return []

    def run(self):
        try:
            self.update_progress.emit(0, "🔍 Fetching city boundaries...")
            city_polygon = self.get_city_polygon()
            if not city_polygon:
                return

            search_points = self.generate_search_points(city_polygon)
            total_points = len(search_points)
            
            params = {
                'radius': 1500,
                'type': self.place_type,
                'fields': 'name,geometry,place_id,rating,user_ratings_total,price_level,opening_hours'
            }

            results = []
            seen_ids = set()
            api_index = 0
            progress_step = 80 / total_points
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for idx, (lat, lng) in enumerate(search_points):
                    if not self.running:
                        break
                    
                    params['location'] = f"{lat},{lng}"
                    api_key = self.API_KEYS[api_index % len(self.API_KEYS)]
                    futures.append(executor.submit(self.get_places_batch, (api_key, params.copy())))
                    
                    if idx % 5 == 0:
                        progress = 10 + (idx / total_points * 80)
                        self.update_progress.emit(int(progress), 
                            f"🌐 Processing point {idx+1}/{total_points}...")
                    
                    api_index += 1
                    time.sleep(random.uniform(0.5, 1.5))

                for idx, future in enumerate(futures):
                    if not self.running:
                        break
                    
                    places = future.result()
                    for place in places:
                        pid = place['place_id']
                        lat = place['geometry']['location']['lat']
                        lng = place['geometry']['location']['lng']
                        
                        if (pid not in seen_ids and 
                            city_polygon.contains(Point(lng, lat))):
                            seen_ids.add(pid)
                            results.append(place)
                            
                    progress = 10 + ((idx + 1) / total_points * 80)
                    self.update_progress.emit(int(progress),
                        f"📥 Collected {len(results)}/{self.MAX_RESULTS} valid places")

                    if len(results) >= self.MAX_RESULTS:
                        break

            df = pd.DataFrame([self.process_result(r) for r in results])
            self.finished.emit(df)

        except Exception as e:
            self.error_occurred.emit(str(e))

    def process_result(self, place):
        return {
            'Name': place.get('name'),
            'Place ID': place.get('place_id'),
            'Address': place.get('vicinity'),
            'Latitude': place['geometry']['location']['lat'],
            'Longitude': place['geometry']['location']['lng'],
            'Rating': place.get('rating'),
            'Total Ratings': place.get('user_ratings_total'),
            'Price Level': place.get('price_level', 'N/A'),
            'Opening Hours': str(place.get('opening_hours', {}).get('weekday_text', []))
        }