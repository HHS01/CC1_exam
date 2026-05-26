import pandas as pd
import requests
import json
import os
import argparse
from pathlib import Path

def fetch_granular_conflicts(iso3="BFA"):
    print(f"🚀 Fetching granular conflict data for {iso3} from HDX (UCDP Source)...")
    
    # Map ISO3 to country names for HDX slugs
    COUNTRY_SLUGS = {
        "BFA": "burkina-faso",
        "MLI": "mali",
        "NER": "niger",
        "SDN": "sudan",
        "UKR": "ukraine",
        "YEM": "yemen"
    }
    
    country_slug = COUNTRY_SLUGS.get(iso3.upper(), iso3.lower())
    search_query = f"ucdp-data-for-{country_slug}"
    dataset_url = f"https://data.humdata.org/api/3/action/package_show?id={search_query}"
    
    try:
        response = requests.get(dataset_url).json()
        if not response.get("success"):
            print(f"✗ Dataset {search_query} not found on HDX.")
            return

        # 2. Find CSV resource
        resources = response["result"]["resources"]
        csv_resource = next((r for r in resources if r["format"].lower() == "csv"), None)
        
        if not csv_resource:
            print(f"✗ No CSV resource found for {search_query}.")
            return

        download_url = csv_resource["url"]
        print(f"  → Downloading from: {download_url}")
        
        df = pd.read_csv(download_url)
        print(f"  ✓ Downloaded {len(df)} records.")

        # 3. Clean and Filter
        # UCDP columns: year, adm_1, adm_2, latitude, longitude, best (fatalities), date_start
        df = df.rename(columns={
            'adm_1': 'Admin1',
            'adm_2': 'Admin2',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'best': 'Fatalities',
            'year': 'Year'
        })
        
        # Filter by year (2015-2026)
        df = df[(df['Year'] >= 2015) & (df['Year'] <= 2026)]
        
        # Add 'Events' count (1 for each row in granular data)
        df['Events'] = 1
        
        # Convert date_start to Month name
        if 'date_start' in df.columns:
            df['Month'] = pd.to_datetime(df['date_start']).dt.strftime('%B')
        else:
            df['Month'] = "Unknown"

        # 4. Save to TEMP
        out_path = Path("TEMP/granular_conflicts.csv")
        df[['Year', 'Month', 'Admin1', 'Admin2', 'Latitude', 'Longitude', 'Events', 'Fatalities']].to_csv(out_path, index=False)
        
        print(f"✅ Success! Saved granular data to {out_path}")
        print(f"   Time range: {df['Year'].min()} - {df['Year'].max()}")
        print(f"   Total incidents: {len(df)}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iso3", default="BFA", help="ISO3 code of the country")
    args = parser.parse_args()
    fetch_granular_conflicts(args.iso3)
