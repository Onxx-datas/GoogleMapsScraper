Google Places API Scraper
This script scrapes data using the Google Places API and extracts useful details about hospitals in a given location. (for example!)

🔥 FEATURES 🔥

✅Fetches hospital names, cordinates, phone number, rating, total ratings.
✅Uses Google Places API to retrieve data.
✅Saves received data into .xlsx(Excel) file inside of folder with actual scraper.
✅Applies custom styling to your Excel file through xlsx_styling.
✅Agrees completely with Terms of Use of Google Places API.

🛠 REQUIREMENTS TO USE SCRIPT 🛠

📕Libraries to install
- pip install requests
- pip install openpyxl

🔑Getting API key from Google Places API
- Go to Google Cloud Console
- Go Proejcts and click New Projects
- Give a name to your project
- Enable API to your new created proeject
- Go to credentials and copy your API key
- Paste API key to code's 6th line
  
 ⚙️Adjust scraping settings
- API_KEY = "" - Your API key
- LOCATIONS = [""] - Longtitude and Latitute of city that you want to scrape
- RADIUS = 12000 - Radius of place that you want to scrape
- KEYWORD = "Hospital" - You can enter keyword that you want to scrape (Limit is 5)
- MAX_RESULTS = 60 - You can adjust it also if you want more results to be collected

  📥Setup, Installation, Running and Output
  To download the script, open a terminal (or Command Prompt) and run:
- git clone https://github.com/Onxx-datas/Informations-about-Hospitals-in-Norwich-UK.git
  To navigate to the folder:
- cd Informations-about-Hospitals-in-Norwich-UK
  Ensure you have Python installed (>=3.7). Then, install required libraries:
- pip install requests openpyxl
  Run the script using:
- python info_scraper.py
  After completion, your data will be saved in an Excel file:
- hospitals_in_norwich.xlsx

  📜File Structure
│── 📄 info_scraper.py   # Main script
│── 📄 settings.py       # Configuration file
│── 📄 xlsx_styling.py   # Excel styling module
│── 📄 README.md         # Documentation (this file)

  ‼️Notes
- The script respects API limits by adding delays to avoid blocking.
- Google Places API has a free tier. After some time using same API it may require billing setup
but exceeding the limit may require billing setup. If you purchase paid contract from Google Places API then you'll get more results.
- If results are missing, reduce the search radius or try different keywords.

  📞Contact
- Telegram: https://t.me/from_xd
- Whatsapp: +998931215597
- Email: kalabiq1@gmail.com
- Phone number: +998931215597
- Instagram: @kom1lo.v

Best regards, ENJOY!
Abdulaziz🙂



