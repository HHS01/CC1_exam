import pandas as pd
import json
import os
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ISO3 = os.environ.get("PIPELINE_ISO3", "BFA")

COUNTRY_MAP = {
    "BFA": "Burkina_Faso",
    "MLI": "Mali",
    "NER": "Niger"
}

def export_conflicts_geojson():
    print(f"🚀 Exporting GRANULAR conflict events GeoJSON for {ISO3}...")
    
    in_path = Path(f"data/clean/acled/HRP_2_countries/{COUNTRY_MAP.get(ISO3, 'Burkina_Faso')}_geocoded.csv")
    out_path = Path("artifacts/conflicts.geojson")
    
    if not in_path.exists():
        print(f"✗ ACLED file not found: {in_path}")
        return

    df = pd.read_csv(in_path)
    
    # Filter for valid coordinates
    df = df.dropna(subset=['Latitude', 'Longitude'])
    
    df['Year'] = df['Year'].astype(int)
    df['Events'] = df['Events'].fillna(0).astype(int)
    df['Fatalities'] = df['Fatalities'].fillna(0).astype(int)

    # Convert to GeoJSON features
    features = []
    for _, row in df.iterrows():
        # Only include years within our simulation range
        if not (2015 <= row['Year'] <= 2026):
            continue
            
        feature = {
            "type": "Feature",
            "properties": {
                "year": int(row['Year']),
                "month": row['Month'],
                "admin2": row['Admin2'],
                "events": int(row['Events']),
                "fatalities": int(row['Fatalities'])
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
    
    print(f"✅ Saved {len(features)} granular events to {out_path}")

if __name__ == "__main__":
    export_conflicts_geojson()
