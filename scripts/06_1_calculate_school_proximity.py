import pandas as pd
import json
import os
from pathlib import Path

ISO3 = os.environ.get("PIPELINE_ISO3", "BFA")

def calculate_proximity():
    print(f"🚀 Calculating school proximity to conflict for {ISO3}...")
    # Placeholder for proximity analysis
    # In a real run, this would calculate distance between schools and nearest conflict
    out_path = Path("artifacts/proximity_risk_stats.json")
    out_path.parent.mkdir(exist_ok=True)
    
    stats = {
        "iso3": ISO3,
        "avg_distance_to_conflict_km": 15.4, # Mock data
        "schools_within_5km": 120,
        "last_updated": pd.Timestamp.now().isoformat()
    }
    
    with open(out_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"  ✓ Saved proximity stats to {out_path}")

if __name__ == "__main__":
    calculate_proximity()
