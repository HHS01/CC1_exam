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
        return Path(f"data/clean/acled/HRP_2_countries/{country}.csv")
    for path in base_dir.glob(f"**/{country}_geocoded.csv"):
        return path
    for path in base_dir.glob(f"**/{country}.csv"):
        return path
    return base_dir / f"HRP_2_countries/{country}.csv"

def export_conflicts_geojson():
    print(f"🚀 Exporting HYBRID conflict events GeoJSON for {ISO3} ({COUNTRY})...")
    
    ucdp_path = Path(f"data/raw/conflicts/{ISO3}_granular_conflicts.csv")
    acled_path = find_acled_file(country_safe)
    out_path = Path("artifacts/conflicts.geojson")
    mapping_path = Path("artifacts/admin_mapping.json")

    if not acled_path.exists():
        print(f"✗ ACLED file not found: {acled_path}")
        return

    # 1. Load Admin Mapping
    mapping = {}
    if mapping_path.exists():
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f).get("official_to_acled", {})

    features = []

    # 2. Process UCDP (Granular - 1989 to 2024)
    ucdp_years = set()
    if ucdp_path.exists():
        try:
            df_u = pd.read_csv(ucdp_path)
            if not df_u.empty and 'year' in df_u.columns:
                # Filter for valid records
                df_u = df_u.dropna(subset=['latitude', 'longitude'])
                
                for _, row in df_u.iterrows():
                    # Clean and map province
                    name = str(row.get('adm_2', 'Unknown')).replace(' province', '').replace(' region', '').strip().title()
                    name = mapping.get(name, name)
                    
                    # Numeric Month
                    month = "00"
                    date_str = str(row.get('date_start', ''))
                    if '-' in date_str:
                        month = date_str.split('-')[1]
                    elif '/' in date_str:
                        month = date_str.split('/')[1]

                    features.append({
                        "type": "Feature",
                        "properties": {
                            "year": int(row['year']),
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
                    ucdp_years.add(int(row['year']))
                print(f"  ✓ Added {len(df_u)} granular UCDP records.")
        except Exception as e:
            print(f"  ⚠ Error processing UCDP file: {e}")

    # 3. Process ACLED (Aggregated - use as fallback for missing years)
    df_a = pd.read_csv(acled_path)
    
    # We use ACLED for:
    # 1. Years not covered by UCDP (e.g. 2025, 2026)
    # 2. As a complete fallback if UCDP had no records
    if not ucdp_years:
        # Fallback to ALL ACLED years
        df_a_filtered = df_a[df_a['Events'] > 0]
        print(f"  [Info] UCDP missing. Falling back to ACLED for all years.")
    else:
        # Use ACLED for years UCDP doesn't have
        df_a_filtered = df_a[(df_a['Events'] > 0) & (~df_a['Year'].isin(ucdp_years))]
        print(f"  [Info] Using ACLED for years: {sorted(list(set(df_a_filtered['Year'].unique())))}")
    
    # Month Map for ACLED names to numbers
    MONTH_MAP = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04',
        'May': '05', 'June': '06', 'July': '07', 'August': '08',
        'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }

    for _, row in df_a_filtered.iterrows():
        # Clean and map province for ACLED as well
        acled_name = str(row['Admin2']).strip().title()
        mapped_name = mapping.get(acled_name, acled_name)

        features.append({
            "type": "Feature",
            "properties": {
                "year": int(row['Year']),
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
    print(f"  ✓ Added {len(df_a_filtered)} aggregated ACLED records.")

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, separators=(',', ':'))
    
    print(f"✅ Success! Saved {len(features)} total events to {out_path}")

if __name__ == "__main__":
    export_conflicts_geojson()
