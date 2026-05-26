"""
06_4_aggregate_at_risk_schools.py
================================
Aggregates individual school risk scores into province-level annual summaries.
Used by the interactive map to show time-series trends and markers.

Input: artifacts/school_vulnerability_scores.json
Output: artifacts/province_at_risk_stats.json
"""

import json
import os
import pandas as pd
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ISO3    = os.environ.get("PIPELINE_ISO3", "BFA")
COUNTRY = os.environ.get("PIPELINE_COUNTRY", "Burkina Faso")

def aggregate_at_risk_schools():
    print(f"🚀 Aggregating at-risk school statistics for {ISO3} ({COUNTRY})...")
    
    # Load data
    score_path = Path("artifacts/school_vulnerability_scores.json")
    if not score_path.exists():
        print(f"✗ Score data missing: {score_path}")
        return

    with open(score_path, 'r', encoding='utf-8') as f:
        scores = json.load(f)

    # Load Dynamic Mapping if available
    mapping_path = Path("artifacts/admin_mapping.json")
    official_to_acled = {}
    if mapping_path.exists():
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping_data = json.load(f)
            if mapping_data.get("iso3") == ISO3:
                official_to_acled = mapping_data.get("official_to_acled", {})
                print(f"  [Info] Using name alignment from admin_mapping.json")

    # Structure: { year: { province: { count: int, schools: [...] } } }
    aggregated = {}

    for s in scores:
        province_raw = s.get("province", "Unknown")
        # Align naming (convert GeoJSON/Official name back to Analysis/ACLED name if mapped)
        province = official_to_acled.get(province_raw, province_raw)
        
        v_score = s.get("v_score", 0)
        trauma = s.get("trauma", 0)
        at_risk_years = s.get("at_risk_years", [])
        name = s.get("name", "Unnamed School")
        lat = s.get("lat", 0)
        lon = s.get("lon", 0)

        # Threshold criteria: High risk (v_score > 0.7)
        if v_score > 0.7:
            for year in at_risk_years:
                y_str = str(year)
                if y_str not in aggregated:
                    aggregated[y_str] = {}
                if province not in aggregated[y_str]:
                    aggregated[y_str][province] = {"count": 0, "schools": []}
                
                aggregated[y_str][province]["count"] += 1
                aggregated[y_str][province]["schools"].append({
                    "name": name,
                    "province": province,
                    "lat": lat,
                    "lon": lon,
                    "v_score": v_score,
                    "trauma": trauma
                })

    # Save output
    out_path = Path("artifacts/province_at_risk_stats.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(aggregated, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Success! Saved {len(aggregated)} years of stats to {out_path}")

if __name__ == "__main__":
    aggregate_at_risk_schools()
