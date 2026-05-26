import pandas as pd
import json
import os
import re
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ISO3 = os.environ.get("PIPELINE_ISO3", "BFA")

def export_conflicts_geojson():
    print(f"🚀 Exporting GRANULAR conflict events GeoJSON for {ISO3}...")
    
    in_path = Path(f"data/raw/conflicts/{ISO3}_granular_conflicts.csv")
    out_path = Path("artifacts/conflicts.geojson")
    mapping_path = Path("artifacts/admin_mapping.json")

    if not in_path.exists():
        print(f"✗ Granular conflict file not found: {in_path}")
        return

    df = pd.read_csv(in_path)

    # 1. Clean Names (UCDP specific cleaning)
    # Remove ' region', ' province', ' Province', etc.
    # UCDP columns: adm_1, adm_2
    df['adm_2_clean'] = df['adm_2'].fillna(df['adm_1']).fillna("Unknown")
    df['adm_2_clean'] = df['adm_2_clean'].str.replace(r'\s+province$', '', case=False, regex=True)
    df['adm_2_clean'] = df['adm_2_clean'].str.replace(r'\s+region$', '', case=False, regex=True)
    df['adm_2_clean'] = df['adm_2_clean'].str.strip().str.title()

    # 2. Apply Dynamic Mapping (Official -> ACLED/Dashboard names)
    if mapping_path.exists():
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f).get("official_to_acled", {})
            df['admin2_final'] = df['adm_2_clean'].map(mapping).fillna(df['adm_2_clean'])
            print(f"  ✓ Applied {len(mapping)} name mappings.")
    else:
        df['admin2_final'] = df['adm_2_clean']

    # 3. Create Features (2015 - 2026)
    # UCDP columns: year, date_start, latitude, longitude, best (fatalities)
    df = df[(df['year'] >= 2015) & (df['year'] <= 2026)]
    
    features = []
    for _, row in df.iterrows():
        # Handle month
        month = "Unknown"
        if 'date_start' in row and pd.notna(row['date_start']):
            try:
                month = pd.to_datetime(row['date_start']).strftime('%B')
            except:
                pass
            
        feature = {
            "type": "Feature",
            "properties": {
                "year": int(row['year']),
                "month": month,
                "admin2": str(row['admin2_final']),
                "events": 1,
                "fatalities": int(row['best']) if pd.notna(row['best']) else 0,
                "source": "UCDP"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['longitude']), float(row['latitude'])]
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, separators=(',', ':'))
    
    print(f"✅ Success! Saved {len(features)} granular events to {out_path}")
    print(f"   Time range: {df['year'].min()} - {df['year'].max()}")

if __name__ == "__main__":
    export_conflicts_geojson()
