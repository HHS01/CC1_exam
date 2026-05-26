import pandas as pd
import requests
import json
import os
import argparse
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ISO3 = os.environ.get("PIPELINE_ISO3", "BFA")

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
    
    # Official path in the pipeline
    raw_dir = Path("data/raw/conflicts")
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / f"{iso3}_granular_conflicts.csv"

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

        # 3. Save raw data
        df.to_csv(out_path, index=False)
        print(f"✅ Saved raw granular data to {out_path}")

    except Exception as e:
        print(f"❌ Error fetching granular data: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iso3", default=ISO3, help="ISO3 code of the country")
    args = parser.parse_args()
    fetch_granular_conflicts(args.iso3)
