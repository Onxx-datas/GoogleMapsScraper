import pandas as pd
from geopy.distance import great_circle
import webbrowser
import matplotlib.pyplot as plt

EXCEL_PATH = "places_results.xlsx"
CENTER_COORD = (52.51475784439185, 13.398880854990345)
MAX_DISTANCE_KM = 5

def load_and_clean():
    df = pd.read_excel(EXCEL_PATH)
    
    df['Opening Hours'] = df['Opening Hours'].apply(eval)  
    if 'Reviews Snapshot' in df.columns:
        df['Reviews Snapshot'] = df['Reviews Snapshot'].apply(eval)
    
    return df

def check_geospatial(df):

    df['Distance (km)'] = df.apply(
        lambda row: great_circle(CENTER_COORD, (row['Latitude'], row['Longitude'])).km,
        axis=1
    )
    outliers = df[df['Distance (km)'] > MAX_DISTANCE_KM]
    print(f"\n📍 {len(outliers)}/{len(df)} places are >{MAX_DISTANCE_KM}km from center")
    return outliers[['Name', 'Address', 'Distance (km)']]

def check_opening_hours(df):
    df['Has Hours'] = df['Opening Hours'].apply(len) > 0
    hour_stats = df['Has Hours'].value_counts(normalize=True)
    print(f"\n⏰ Opening Hours Coverage: {hour_stats[True]:.1%} with hours")
    return df[df['Has Hours'] == False][['Name', 'Types']]

def check_price_levels(df):
    price_missing = df['Price Level'].isna().sum()
    print(f"\n💰 Price Levels: {price_missing}/{len(df)} missing ({price_missing/len(df):.1%})")
    
    if 'Price Level' in df.columns:
        df['Price Level'].value_counts().sort_index().plot(
            kind='bar', 
            title='Price Level Distribution (1=€ to 4=€€€€)'
        )
        plt.show()
    
    return df[df['Price Level'].isna()][['Name', 'Types']]

def interactive_validation(df):
    sample = df.sample(5)
    print("\n🔍 Sample Verification (opens in browser):")
    
    for _, row in sample.iterrows():
        url = f"https://www.google.com/maps?q=place_id:{row['Place ID']}"
        print(f"- {row['Name']}: {url}")
        webbrowser.open_new_tab(url)
    
    input("\nPress Enter after verifying samples...")

def generate_report(df):
    with open("data_quality_report.txt", "w") as f:
        f.write("=== DATA QUALITY REPORT ===\n\n")
        
        outliers = check_geospatial(df)
        f.write("COORDINATE OUTLIERS:\n")
        f.write(outliers.to_string() + "\n\n")
        
        no_hours = check_opening_hours(df)
        f.write("PLACES WITHOUT HOURS:\n")
        f.write(no_hours.to_string() + "\n\n")
        
        missing_prices = check_price_levels(df)
        f.write("PLACES WITHOUT PRICE LEVELS:\n")
        f.write(missing_prices.to_string())

if __name__ == "__main__":
    print("🛠️ Loading data...")
    data = load_and_clean()
    
    while True:
        print("\n1. Full report")
        print("2. Check coordinate outliers")
        print("3. Check missing opening hours")
        print("4. Check price levels")
        print("5. Interactive validation")
        print("6. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == "1":
            generate_report(data)
            print("✅ Report saved as data_quality_report.txt")
        elif choice == "2":
            print(check_geospatial(data))
        elif choice == "3":
            print(check_opening_hours(data))
        elif choice == "4":
            print(check_price_levels(data))
        elif choice == "5":
            interactive_validation(data)
        elif choice == "6":
            break