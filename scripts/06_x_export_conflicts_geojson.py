import pandas as pd
import json
import os
import re
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ISO3    = os.environ.get("PIPELINE_ISO3", "BFA")
COUNTRY = os.environ.get("PIPELINE_COUNTRY", "Burkina Faso")

# Sanitize country name for file matching
country_safe = COUNTRY.replace(" ", "_")

def find_acled_file(country: str) -> Path:
    """Search for the country's ACLED CSV in any data/clean/acled/* subdirectory."""
    base_dir = Path("data/clean/acled")
    if not base_dir.exists():
        return Path(f"data/clean/acled/HRP_1_countries/{country}.csv")
    for path in base_dir.glob(f"**/{country}_geocoded.csv"):
        return path
    for path in base_dir.glob(f"**/{country}.csv"):
        return path
    return base_dir / f"HRP_1_countries/{country}.csv"

def export_conflicts_geojson():
    print(f"🚀 Exporting HYBRID conflict events GeoJSON for {ISO3} ({COUNTRY})...")
    
    out_dir = Path("artifacts") / ISO3
    out_dir.mkdir(parents=True, exist_ok=True)

    ucdp_path = Path(f"data/raw/conflicts/{ISO3}_granular_conflicts.csv")
    acled_path = find_acled_file(country_safe)
    out_path = out_dir / "conflicts.geojson"
    mapping_path = out_dir / "admin_mapping.json"

    if not acled_path.exists():
        print(f"✗ ACLED file not found: {acled_path}")
        return

    # 1. Load Admin Mapping
    mapping = {}
    if mapping_path.exists():
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f).get("official_to_acled", {})

    # 2. Load Existing Data (Persistence Strategy)
    # Separated by year to allow easy merging/overwriting
    master_features_by_year = {}
    if out_path.exists():
        print(f"  → Loading existing historical data from {out_path}...")
        try:
            with open(out_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                for feat in old_data.get("features", []):
                    yr = feat["properties"].get("year")
                    if yr:
                        if yr not in master_features_by_year:
                            master_features_by_year[yr] = []
                        master_features_by_year[yr].append(feat)
            print(f"    ✓ Found data for {len(master_features_by_year)} years.")
        except Exception as e:
            print(f"  ⚠ Failed to load existing GeoJSON: {e}")

    # 3. Process New Data (Current CSVs)
    new_features_by_year = {}

    # 3a. Process UCDP (Granular)
    ucdp_years = set()
    if ucdp_path.exists():
        try:
            df_u = pd.read_csv(ucdp_path)
            if not df_u.empty and 'year' in df_u.columns:
                df_u = df_u.dropna(subset=['latitude', 'longitude'])
                for _, row in df_u.iterrows():
                    yr = int(row['year'])
                    if yr not in new_features_by_year: new_features_by_year[yr] = []
                    
                    name = str(row.get('adm_2', 'Unknown')).replace(' province', '').replace(' region', '').strip().title()
                    name = mapping.get(name, name)
                    
                    month = "00"
                    date_str = str(row.get('date_start', ''))
                    if '-' in date_str: month = date_str.split('-')[1]
                    elif '/' in date_str: month = date_str.split('/')[1]

                    new_features_by_year[yr].append({
                        "type": "Feature",
                        "properties": {
                            "year": yr,
                            "month": month,
                            "admin2": name,
                            "events": 1,
                            "fatalities": int(row['best']) if pd.notna(row.get('best')) else 0,
                            "is_granular": True,
                            "source": "UCDP"
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(row['longitude']), float(row['latitude'])]
                        }
                    })
                    ucdp_years.add(yr)
                print(f"  ✓ Processed UCDP records for years: {sorted(list(ucdp_years))}")
        except Exception as e:
            print(f"  ⚠ Error processing UCDP file: {e}")

    # 3b. Process ACLED (Aggregated fallback)
    df_a = pd.read_csv(acled_path)
    # We use ACLED if UCDP is missing for that year OR if UCDP has no records at all
    for yr, group in df_a.groupby("Year"):
        yr = int(yr)
        if yr not in ucdp_years:
            if yr not in new_features_by_year: new_features_by_year[yr] = []
            
            MONTH_MAP = {
                'January': '01', 'February': '02', 'March': '03', 'April': '04',
                'May': '05', 'June': '06', 'July': '07', 'August': '08',
                'September': '09', 'October': '10', 'November': '11', 'December': '12'
            }

            for _, row in group.iterrows():
                if row['Events'] <= 0: continue
                
                acled_name = str(row['Admin2']).strip().title()
                mapped_name = mapping.get(acled_name, acled_name)

                new_features_by_year[yr].append({
                    "type": "Feature",
                    "properties": {
                        "year": yr,
                        "month": MONTH_MAP.get(str(row['Month']), '00'),
                        "admin2": mapped_name,
                        "events": int(row['Events']),
                        "fatalities": int(row['Fatalities']),
                        "is_granular": False,
                        "source": "ACLED"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(row['Longitude']), float(row['Latitude'])]
                    }
                })
    
    # 4. Merge Logic (Overwrite overlap, preserve history)
    # Start with historical years
    final_features = []
    
    # Years to keep from existing data (those not present in the new CSVs)
    preserved_years = [y for y in master_features_by_year if y not in new_features_by_year]
    for y in preserved_years:
        final_features.extend(master_features_by_year[y])
    
    # Years to take from new data
    for y in sorted(new_features_by_year.keys()):
        final_features.extend(new_features_by_year[y])

    print(f"  → Merging complete. Preserved {len(preserved_years)} historical years. Updated {len(new_features_by_year)} years.")

    # 5. Save
    geojson = {
        "type": "FeatureCollection",
        "features": final_features
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, separators=(',', ':'))
    
    print(f"✅ Success! Saved {len(final_features)} total events to {out_path}")

if __name__ == "__main__":
    export_conflicts_geojson()
