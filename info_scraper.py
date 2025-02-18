import requests # To send requests to the Places API
import time # We need it to use in the future for example time.sleep(3) to stop code block for 3 seconds 
import openpyxl # This is needed to handle .xlsx(Excel) files
import xlsx_styling # This is another hand made .py code stylings

API_KEY = "" # API key from Places API (Google Cloud Console), (❗❗ PLACE YOURS ❗❗)
LOCATIONS = ["52.630886, 1.297355"] # Longtitude and Latitude from place that we want to scrape
RADIUS = 100000  # Radius from given Longtitude and Latitude (We can adjust it), (How big radius is how more results we will collect)
KEYWORD = "Hospital" # Searches given keyword from buildings inside of given radius
MAX_RESULTS = 18000 # Maximum result we need to collect

hospitals = [] # List to collect informations temporarly

def get_phone_number(place_id): # Creating function to get phone number from Places API
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=formatted_phone_number&key={API_KEY}" # Details URL inside of Places API
    response = requests.get(details_url) # To send request to the details URL
    if response.status_code == 200: # If response code is not 200 it means request was sent unsuccessfully and response is also good
        details_data = response.json() # Saves details data to the JSON format
        return details_data.get("result", {}).get("formatted_phone_number", "N/A") # Phone number scraped Separately so that's why we need to add phone number into result
    return "N/A" # If response code is not 200 it gives us N/A (Not Available) response
for location in LOCATIONS: # Loops through all locations from given LOCATION long/Lat
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={RADIUS}&keyword={KEYWORD}&key={API_KEY}" # Creating Google API request URL
    while url and len(hospitals) < MAX_RESULTS: # Keeps making request until: url="" exists, hospitals has less results than 120
        response = requests.get(url) # Sending request to get response about hospital data
        if response.status_code != 200: # If response code is 200 (Successfull) it will print error message
            print("Error fetching data:", response.status_code, response.text) # Printing that eroor message
            break # Stops code block if response code is 200
        data = response.json() # Gets informations about hospitals from API JSON
        results = data.get("results", []) # And saves it into results
        for place in results: # Loops for each places from response
            if len(hospitals) >= MAX_RESULTS: # If place result reaches MAX_RESULTS...
                break # It breaks because we gave maximum data we want (120)
            name = place.get("name", "N/A") # Extracting hospital name
            location_data = place.get("geometry", {}).get("location", {}) # Extracting hospital coordinates (Long/Lat)
            lat = location_data.get("lat", "N/A") # Extracting hospital coordinates (Long/Lat)
            lng = location_data.get("lng", "N/A") # Extracting hospital coordinates (Long/Lat)
            coordinates = f"{lat}, {lng}" # Extracting hospital coordinates (Long/Lat)
            rating = place.get("rating", "N/A")  # Extracting hospital rates (Stars)
            total_ratings = place.get("user_ratings_total", "N/A") # Extracting all given ratings
            place_id = place.get("place_id", None) # Extracting unique ID to further informations
            phone_number = get_phone_number(place_id) if place_id else "Not Available" # Extracts phone number from self made-function named phone_number. N/A if number not available
            hospitals.append([name, coordinates, phone_number, rating, total_ratings]) # Appending these scraped information to the hospitals list
        next_page_token = data.get("next_page_token") # Next page to get more data
        if next_page_token: # If next page available...
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={next_page_token}&key={API_KEY}" # Get the URL from that available page
            time.sleep(2) # Wait for 2 seconds (For not activating anti-bot, reCAPTCHA's)
        else: # If no page
            url = None # Change current URL into None
file_name = "hospitals_in_norwich.xlsx" # Entering .xlsx name while saving
wb = openpyxl.Workbook() # Using Workbook inside of openpyxl as a "wb" variable
ws = wb.active # Activating this "wb" using "ws"
ws.title = "Hospitals" # Adjusting hospital list name title as a Hospital
ws.append(["Name", "Coordinates (Lat, Lng)", "Phone Number", "Rating", "Total Ratings"]) # Giving each column it's unique name
for hospital in hospitals: # Saving each hospital informations into...
    ws.append(hospital) # hospital informations will be appended into Each column
wb.save(file_name) # Saving all this informations into file_name (hospitals_in_norwich.xlsx)
print(f"💾 Hospital data saved to {file_name}") # All code blocks worked successfully it prints "💾 Hospital data saved to ..."
xlsx_styling.apply_styles(file_name) # Applying recent created styling .py file into our .xlsx file
print("✅ Check Excel file to see scraped information") # Final success message to user