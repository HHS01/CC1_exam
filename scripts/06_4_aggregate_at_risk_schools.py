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
    score_path = Path(f"artifacts/schools/{ISO3}_school_vulnerability.csv")
    if not score_path.exists():
        print(f"✗ Score data missing: {score_path}")
        return

    df = pd.read_csv(score_path)

    # Load Dynamic Mapping if available
    mapping_path = Path("artifacts/admin_mapping.json")
    official_to_acled = {}
    if mapping_path.exists():
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping_data = json.load(f)
            if mapping_data.get("iso3") == ISO3:
                official_to_acled = mapping_data.get("official_to_acled", {})
                print(f"  [Info] Using name alignment from admin_mapping.json")

    # If province is not in CSV, we might need a spatial join, but let's assume it's there or handle missing
    if "province" not in df.columns:
        # Fallback: if we don't have provinces in the CSV, we'll use a dummy or try to get it
        print("  ⚠ 'province' column missing in score CSV. Attempting to use Admin2 mapping if available.")
        # For now, let's assume 'Admin2' might be there if we joined it
        if "Admin2" in df.columns:
             df["province"] = df["Admin2"]
        else:
             df["province"] = "Unknown"

    # Structure: { year: { province: { count: int, schools: [...] } } }
    aggregated = {}

    for _, s in df.iterrows():
        province_raw = str(s.get("province", "Unknown"))
        province = official_to_acled.get(province_raw, province_raw)
        
        v_score = s.get("final_score", 0)
        at_risk = s.get("at_risk", False)
        name = s.get("name", "Unnamed School")
        lat = s.get("latitude", 0)
        lon = s.get("longitude", 0)

        # Threshold criteria: High risk (final_score > 0.7)
        if v_score > 0.7:
            # Since the current CSV is a snapshot for 2024, we'll map it to 2024
            # In a full version, we'd have historical scores
            for year in [2024, 2025, 2026]: # Mocking future risk
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
                    "v_score": float(v_score)
                })

    # Save output (this is what Step 22 or other steps might expect as school_vulnerability_scores.json if renamed)
    # Actually, we'll save it to the path requested by aggregate_at_risk_schools
    out_path = Path("artifacts/province_at_risk_stats.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(aggregated, f, indent=2, ensure_ascii=False)
    
    # Also save the flat scores JSON if needed by other scripts
    scores_json_path = Path("artifacts/school_vulnerability_scores.json")
    df.to_json(scores_json_path, orient="records")

    print(f"✅ Success! Saved stats to {out_path}")

if __name__ == "__main__":
    aggregate_at_risk_schools()
