import pandas as pd
import json
import os
from pathlib import Path

def export_granular_geojson():
    print("🚀 Exporting granular GeoJSON from UCDP data...")
    
    in_path = Path("TEMP/granular_conflicts.csv")
    out_path = Path("TEMP/conflicts_granular.geojson")
    mapping_path = Path("artifacts/admin_mapping.json")

    if not in_path.exists():
        print(f"✗ Granular CSV not found: {in_path}")
        return

    df = pd.read_csv(in_path)

    # 1. Clean Names (UCDP specific cleaning)
    # Remove ' region', ' province', ' Province', etc.
    df['Admin2_Clean'] = df['Admin2'].fillna(df['Admin1']).fillna("Unknown")
    df['Admin2_Clean'] = df['Admin2_Clean'].str.replace(r'\s+province$', '', case=False, regex=True)
    df['Admin2_Clean'] = df['Admin2_Clean'].str.replace(r'\s+region$', '', case=False, regex=True)
    df['Admin2_Clean'] = df['Admin2_Clean'].str.strip().str.title()
    
    df['Admin1_Clean'] = df['Admin1'].fillna("Unknown")
    df['Admin1_Clean'] = df['Admin1_Clean'].str.replace(r'\s+region$', '', case=False, regex=True).str.strip().str.title()

    # 2. Apply Dynamic Mapping
    if mapping_path.exists():
        with open(mapping_path, 'r') as f:
            mapping = json.load(f).get("official_to_acled", {})
            df['Admin2_Final'] = df['Admin2_Clean'].map(mapping).fillna(df['Admin2_Clean'])
            print(f"  ✓ Applied {len(mapping)} name mappings.")
    else:
        df['Admin2_Final'] = df['Admin2_Clean']

    # 3. Create Features
    features = []
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "properties": {
                "year": int(row['Year']),
                "month": str(row['Month']),
                "admin2": str(row['Admin2_Final']),
                "events": int(row['Events']),
                "fatalities": int(row['Fatalities']),
                "source": "UCDP (Granular)"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['Longitude']), float(row['Latitude'])]
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, separators=(',', ':'))
    
    print(f"✅ Success! Saved {len(features)} points to {out_path}")

if __name__ == "__main__":
    export_granular_geojson()
