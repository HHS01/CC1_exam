import pandas as pd
import os
from pathlib import Path

ISO3 = os.environ.get("PIPELINE_ISO3", "BFA")

def calculate_density_gap():
    print(f"🚀 Calculating school density gap for {ISO3}...")
    # Mock density gap calculation
    out_path = Path("artifacts/province_school_fragility.csv")
    out_path.parent.mkdir(exist_ok=True)
    
    # Create mock data if it doesn't exist to allow downstream steps to run
    # In a full run, this would use WorldPop data
    data = [
        {"Region": "Admin2_A", "year": 2024, "school_fragility_score": 0.45, "school_count": 50, "schools_per_1000_children": 0.8, "school_age_pop": 62500},
        {"Region": "Admin2_B", "year": 2024, "school_fragility_score": 0.82, "school_count": 12, "schools_per_1000_children": 0.2, "school_age_pop": 60000}
    ]
    df = pd.DataFrame(data)
    df.to_csv(out_path, index=False)
    print(f"  ✓ Saved density gap analysis to {out_path}")

if __name__ == "__main__":
    calculate_density_gap()
