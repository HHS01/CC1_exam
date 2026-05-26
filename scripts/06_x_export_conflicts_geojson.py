import pandas as pd
import json
import os
import re
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ISO3 = os.environ.get("PIPELINE_ISO3", "BFA")

def export_conflicts_geojson():
    print(f"🚀 Exporting HYBRID conflict events GeoJSON for {ISO3}...")
    
    ucdp_path = Path(f"data/raw/conflicts/{ISO3}_granular_conflicts.csv")
    acled_path = Path(f"data/clean/acled/HRP_2_countries/Burkina_Faso_geocoded.csv")
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

    # 2. Process UCDP (Granular - 2016 to 2024)
    if ucdp_path.exists():
        df_u = pd.read_csv(ucdp_path)
        # Filter for years where UCDP is the primary source
        df_u = df_u[(df_u['year'] >= 2016) & (df_u['year'] <= 2024)]
        
        for _, row in df_u.iterrows():
            # Clean and map province
            name = str(row['adm_2']).replace(' province', '').replace(' region', '').strip().title()
            name = mapping.get(name, name)
            
            # Numeric Month (e.g. '05')
            month = "00"
            if '-' in str(row['date_start']):
                month = str(row['date_start']).split('-')[1]

            features.append({
                "type": "Feature",
                "properties": {
                    "year": int(row['year']),
                    "month": month,
                    "admin2": name,
                    "events": 1,
                    "fatalities": int(row['best']) if pd.notna(row['best']) else 0,
                    "is_granular": True
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row['longitude']), float(row['latitude'])]
                }
            })
        print(f"  ✓ Added {len(df_u)} granular UCDP records.")

    # 3. Process ACLED (Aggregated - 2015, 2025, 2026)
    df_a = pd.read_csv(acled_path)
    # Filter for years where UCDP is missing but we need data
    df_a = df_a[(df_a['Year'] == 2015) | (df_a['Year'] == 2025) | (df_a['Year'] == 2026)]
    # Only keep rows with actual events
    df_a = df_a[df_a['Events'] > 0]
    
    # Month Map for ACLED names to numbers
    MONTH_MAP = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04',
        'May': '05', 'June': '06', 'July': '07', 'August': '08',
        'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }

    for _, row in df_a.iterrows():
        features.append({
            "type": "Feature",
            "properties": {
                "year": int(row['Year']),
                "month": MONTH_MAP.get(str(row['Month']), '00'),
                "admin2": str(row['Admin2']),
                "events": int(row['Events']),
                "fatalities": int(row['Fatalities']),
                "is_granular": False
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['Longitude']), float(row['Latitude'])]
            }
        })
    print(f"  ✓ Added {len(df_a)} aggregated ACLED records for 2015, 2025, 2026.")

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, separators=(',', ':'))
    
    print(f"✅ Success! Saved {len(features)} total events to {out_path}")

if __name__ == "__main__":
    export_conflicts_geojson()
