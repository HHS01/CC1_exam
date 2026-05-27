import os
import pandas as pd
from pathlib import Path

ISO3 = os.environ.get("PIPELINE_ISO3", "BFA")

def fetch_granular():
    print(f"🚀 Searching for granular UCDP data for {ISO3}...")
    # This is a placeholder that checks if the file exists
    # In a real scenario, this would call the UCDP API
    raw_dir = Path("data/raw/conflicts")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    target = raw_dir / f"{ISO3}_granular_conflicts.csv"
    if target.exists():
        print(f"  ✓ Found existing granular data at {target}")
    else:
        print(f"  ⚠ No granular UCDP data found for {ISO3}. Creating empty placeholder.")
        df = pd.DataFrame(columns=['id', 'year', 'date_start', 'latitude', 'longitude', 'best', 'adm_1', 'adm_2'])
        df.to_csv(target, index=False)

if __name__ == "__main__":
    fetch_granular()
