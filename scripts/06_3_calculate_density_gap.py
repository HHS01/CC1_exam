import pandas as pd
import geopandas as gpd
import os
import json
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ISO3    = os.environ.get("PIPELINE_ISO3", "NGA")
COUNTRY = os.environ.get("PIPELINE_COUNTRY", "Nigeria")

def calculate_density_gap():
    print(f"🚀 Calculating continuous relative school density gap for {ISO3} ({COUNTRY})...")
    
    # 1. Paths
    schools_path = Path(f"data/clean/schools/final_cleaned_schools_{ISO3}.csv")
    pop_path     = Path(f"data/clean/nga_pop_density/nga_pop_2020.json") 
    bounds_path  = Path(f"data/raw/boundaries/{ISO3}_admin2.geojson")
    out_path     = Path("artifacts/province_school_fragility.csv")

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
    merged = bounds[[name_col]].merge(school_counts, on=name_col, how="left").merge(pop_counts, on=name_col, how="left")
    merged["school_count"] = merged["school_count"].fillna(0)
    merged["total_pop"] = merged["total_pop"].fillna(0)
    
    # Estimate school-age population (25% constant proxy)
    merged["school_age_pop"] = merged["total_pop"] * 0.25
    
    # Schools per 1000 children
    merged["schools_per_1000_children"] = (merged["school_count"] / (merged["school_age_pop"] / 1000)).replace([float('inf'), -float('inf')], 0).fillna(0)
    
    # 6. RELATIVE FRAGILITY LOGIC
    # We use the 80th Percentile of the country's own data as the sufficiency target
    target = merged["schools_per_1000_children"].quantile(0.8)
    if target <= 0: target = 1.0 # Safety fallback
    
    print(f"  → Sufficiency Target (80th Percentile): {target:.3f} schools/1k children")
    
    # Continuous Score: 1 - (Ratio / Target), clipped 0-1
    merged["school_fragility_score"] = (1 - (merged["schools_per_1000_children"] / target)).clip(0, 1)

    # 7. MULTI-YEAR PROJECTION
    # Apply this structural baseline to all years in the timeline (2015-2026)
    # This allows the structural bar to show alongside dynamic conflict bars
    years = list(range(2015, 2027))
    all_years_data = []
    
    for yr in years:
        yr_df = merged.copy()
        yr_df["year"] = yr
        all_years_data.append(yr_df)
        
    final_df = pd.concat(all_years_data)
    final_df = final_df.rename(columns={name_col: "Region"})
    
    final_cols = ["Region", "year", "school_fragility_score", "school_count", "schools_per_1000_children", "school_age_pop"]
    final_df[final_cols].to_csv(out_path, index=False)
    
    print(f"  ✓ Saved continuous relative analysis for {len(merged)} provinces across {len(years)} years to {out_path}")

if __name__ == "__main__":
    calculate_density_gap()
