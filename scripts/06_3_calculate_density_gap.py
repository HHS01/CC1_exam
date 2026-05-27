import pandas as pd
import geopandas as gpd
import os
import json
import requests
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ISO3    = os.environ.get("PIPELINE_ISO3", "BFA")
COUNTRY = os.environ.get("PIPELINE_COUNTRY", "Burkina Faso")

def get_growth_rates(iso3):
    """Fetch annual population growth % from World Bank API."""
    print(f"  → Fetching annual growth rates from World Bank for {iso3}...")
    try:
        # Fetching a wide range to cover 2015-2026
        url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/SP.POP.GROW?format=json&per_page=100"
        res = requests.get(url, timeout=10)
        data = res.json()
        if len(data) > 1:
            rates = {int(item['date']): item['value']/100 for item in data[1] if item['value'] is not None}
            return rates
    except Exception as e:
        print(f"  ⚠ Growth rate fetch failed: {e}. Using fallback 2.3%.")
    return {}

def calculate_density_gap():
    print(f"🚀 Calculating continuous relative school density gap for {ISO3} ({COUNTRY})...")
    
    # 1. Paths
    schools_path = Path(f"data/clean/schools/schools_{ISO3}.csv")
    pop_path     = Path(f"data/clean/{ISO3.lower()}_pop_density/{ISO3.lower()}_pop_2020.json") 
    bounds_path  = Path(f"data/raw/boundaries/{ISO3}_admin2.geojson")
    
    out_dir = Path("artifacts") / ISO3
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "province_school_fragility.csv"

    if not all([schools_path.exists(), pop_path.exists(), bounds_path.exists()]):
        print("✗ Missing input data. Ensure 02_x, 04_1, and raw boundaries exist.")
        return

    # 2. Load Data
    schools_df = pd.read_csv(schools_path)
    with open(pop_path, 'r') as f:
        pop_data = json.load(f)
    bounds = gpd.read_file(bounds_path)

    # 3. Process Schools per Province
    schools_gdf = gpd.GeoDataFrame(
        schools_df, 
        geometry=gpd.points_from_xy(schools_df.longitude, schools_df.latitude),
        crs="EPSG:4326"
    )
    
    name_col = next(
        (c for c in bounds.columns
         if any(x in c.lower() for x in ["adm2_en", "adm2_name", "name_2", "shapename", "admin2name"])),
        bounds.columns[0]
    )

    if bounds.crs != schools_gdf.crs:
        bounds = bounds.to_crs(schools_gdf.crs)
    
    schools_joined = gpd.sjoin(schools_gdf, bounds[[name_col, "geometry"]], how="inner", predicate="within")
    school_counts = schools_joined.groupby(name_col).size().reset_index(name="school_count")

    # 4. Process Population per Province
    pop_points = []
    for entry in pop_data["data"]:
        pop_points.append({"lat": entry[0], "lon": entry[1], "pop_density": entry[2]})
    
    pop_df = pd.DataFrame(pop_points)
    pop_gdf = gpd.GeoDataFrame(
        pop_df,
        geometry=gpd.points_from_xy(pop_df.lon, pop_df.lat),
        crs="EPSG:4326"
    )
    
    pop_joined = gpd.sjoin(pop_gdf, bounds[[name_col, "geometry"]], how="inner", predicate="within")
    pop_counts = pop_joined.groupby(name_col)["pop_density"].sum().reset_index(name="total_pop")

    # 5. Merge and Calculate Ratio
    # This 'merged' represents our anchor year (2020)
    anchor_2020 = bounds[[name_col]].merge(school_counts, on=name_col, how="left").merge(pop_counts, on=name_col, how="left")
    anchor_2020["school_count"] = anchor_2020["school_count"].fillna(0)
    anchor_2020["total_pop"] = anchor_2020["total_pop"].fillna(0)
    
    # Estimate school-age population (25% constant proxy)
    anchor_2020["school_age_pop_2020"] = anchor_2020["total_pop"] * 0.25
    
    # 6. DYNAMIC CHAIN EXTRAPOLATION (2015-2026)
    rates = get_growth_rates(ISO3)
    default_rate = 0.023 # 2.3% fallback
    
    years = list(range(2015, 2027))
    all_years_data = []

    print(f"  → Extrapolating population using the Chain Method (Anchor: 2020)...")
    for _, province_row in anchor_2020.iterrows():
        p_name = province_row[name_col]
        pop_history = {2020: province_row["school_age_pop_2020"]}
        
        # Forward Chain (2021-2026)
        for yr in range(2021, 2027):
            # Use specific rate if available, else latest available
            rate = rates.get(yr, rates.get(max(rates.keys()) if rates else 2024, default_rate))
            pop_history[yr] = pop_history[yr-1] * (1 + rate)
            
        # Backward Chain (2015-2019)
        # 2019 pop = 2020 pop / (1 + 2020 growth)
        for yr in range(2019, 2014, -1):
            rate = rates.get(yr+1, rates.get(min(rates.keys()) if rates else 2015, default_rate))
            pop_history[yr] = pop_history[yr+1] / (1 + rate)

        for yr in years:
            all_years_data.append({
                "Region": p_name,
                "year": yr,
                "school_count": province_row["school_count"],
                "school_age_pop": pop_history[yr]
            })

    final_df = pd.DataFrame(all_years_data)
    
    # 7. RELATIVE FRAGILITY LOGIC (Per Year)
    def calculate_annual_scores(group):
        # The 'year' column is part of the group
        group["schools_per_1000_children"] = (group["school_count"] / (group["school_age_pop"] / 1000)).replace([float('inf'), -float('inf')], 0).fillna(0)
        target = group["schools_per_1000_children"].quantile(0.8)
        if target <= 0: target = 1.0
        group["school_fragility_score"] = (1 - (group["schools_per_1000_children"] / target)).clip(0, 1)
        return group

    final_df = final_df.groupby("year", group_keys=False).apply(calculate_annual_scores)
    
    # Force recovery of 'year' if it's trapped in the index
    if "year" not in final_df.columns:
        final_df = final_df.reset_index()
        if "year" not in final_df.columns and "index" in final_df.columns:
            final_df = final_df.rename(columns={"index": "year"})
        elif "year" not in final_df.columns and "level_0" in final_df.columns:
             final_df = final_df.rename(columns={"level_0": "year"})

    # Absolute fallback: if we still don't have it, we can't proceed
    if "year" not in final_df.columns:
        print(f"  ⚠ CRITICAL: 'year' column lost. Columns: {final_df.columns}")
        return
    
    final_cols = ["Region", "year", "school_fragility_score", "school_count", "schools_per_1000_children", "school_age_pop"]
    final_df[final_cols].to_csv(out_path, index=False)
    
    print(f"  ✓ Saved Dynamic Bi-Directional Chain Analysis for {len(anchor_2020)} provinces across {len(years)} years to {out_path}")

if __name__ == "__main__":
    calculate_density_gap()
