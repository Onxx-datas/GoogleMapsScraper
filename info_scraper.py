import requests  # To send HTTP requests to the Google Places API
import time  # To add delays (e.g., avoid triggering API rate limits)
import openpyxl  # To create and handle Excel (.xlsx) files
import xlsx_styling  # Custom module to style the Excel output file
from settings import API_KEY, LOCATIONS, RADIUS, KEYWORD, MAX_RESULTS # Importing settings from settings.py
hospitals = [] # Saves recived data temporarl
def get_phone_number(place_id): # Creating func that gets phone numbers
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=formatted_phone_number&key={API_KEY}"
    response = requests.get(details_url)  # Send request to fetch place details
    if response.status_code == 200:  # If request is successfull
        details_data = response.json()  # Convert response to JSON format
        return details_data.get("result", {}).get("formatted_phone_number", "N/A")  # Extract phone number or return "N/A"
    return "N/A"  # Return "N/A" if request fails
# Loop through each location in the LOCATIONS list
for location in LOCATIONS:
    # Construct the API request URL for searching nearby hospitals
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={RADIUS}&keyword={KEYWORD}&key={API_KEY}"
    # Continue making API requests until no more results or max limit is reached
    while url and len(hospitals) < MAX_RESULTS:
        response = requests.get(url)  # Send API request
        # If response is unsuccessful, print error and stop the loop
        if response.status_code != 200:
            print("Error fetching data:", response.status_code, response.text)
            break
        data = response.json()  # Convert response to JSON format
        results = data.get("results", [])  # Extract hospital data from response
        # Loop through each place (hospital) in the response
        for place in results:
            if len(hospitals) >= MAX_RESULTS:  # Stop collecting if max results reached
                break  
            # Extract hospital details
            name = place.get("name", "N/A")  # Hospital name
            location_data = place.get("geometry", {}).get("location", {})  # Location details
            lat = location_data.get("lat", "N/A")  # Latitude
            lng = location_data.get("lng", "N/A")  # Longitude
            coordinates = f"{lat}, {lng}"  # Combine Lat and Lng into a single string
            rating = place.get("rating", "N/A")  # Star rating
            total_ratings = place.get("user_ratings_total", "N/A")  # Total number of ratings
            place_id = place.get("place_id", None)  # Unique ID of the place
            # Fetch phone number using place_id, if available
            phone_number = get_phone_number(place_id) if place_id else "Not Available"
            # Append collected data to the hospitals list
            hospitals.append([name, coordinates, phone_number, rating, total_ratings])
        # Check if there's another page of results (pagination)
        next_page_token = data.get("next_page_token")
        if next_page_token:  # If more results exist...
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={next_page_token}&key={API_KEY}"
            time.sleep(2)  # Wait 2 seconds before next request (to prevent API blocking)
        else:
            url = None  # Stop if there are no more pages
# Create an Excel file to store the collected hospital data
file_name = "hospitals_in_norwich.xlsx"
wb = openpyxl.Workbook()  # Create a new Excel workbook
ws = wb.active  # Select the active sheet
ws.title = "Hospitals"  # Rename sheet to "Hospitals"
# Add column headers to the Excel sheet
ws.append(["Name", "Coordinates (Lat, Lng)", "Phone Number", "Rating", "Total Ratings"])
# Write each hospital's data into the Excel sheet
for hospital in hospitals:
    ws.append(hospital)
# Save the Excel file with collected data
wb.save(file_name)
print(f"💾 Hospital data saved to {file_name}")  # Confirmation message
# Apply styling using the custom xlsx_styling module
xlsx_styling.apply_styles(file_name)
print("✅ Check Excel file to see scraped information")  # Final success message
