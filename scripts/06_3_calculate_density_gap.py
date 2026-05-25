import pandas as pd
import geopandas as gpd
import os
import json
import argparse

def get_school_age_pct_info(iso3):
    """
    Fetches the 'Population ages 0-14 (% of total population)' from master_education.csv
    Returns (dict {year: pct}, country_average_pct)
    """
    edu_path = "data/clean/education/master_education.csv"
    GLOBAL_DEFAULT = 0.44
    if not os.path.exists(edu_path):
        print(f"⚠️  {edu_path} not found. Using global default {GLOBAL_DEFAULT:.2%}")
        return {}, GLOBAL_DEFAULT

    try:
        # The file appears to have a header based on the head command
        df = pd.read_csv(edu_path)
        
        # Ensure 'value' is numeric, coercing errors to NaN
        df["value"] = pd.to_numeric(df["value"], errors='coerce')
        
        # Filter for country and correct indicator
        mask = (df["iso3"] == iso3) & (df["indicator"] == "Population ages 0-14 (% of total population)")
        subset = df[mask].dropna(subset=["value"])
        
        if subset.empty:
            print(f"⚠️  No data found for {iso3}. Using global default {GLOBAL_DEFAULT:.2%}")
            return {}, GLOBAL_DEFAULT
            
        # Build dict {year: value/100}
        lookup = dict(zip(subset["year"].astype(int), subset["value"] / 100.0))
        country_avg = subset["value"].mean() / 100.0
        return lookup, country_avg
    except Exception as e:
        print(f"⚠️  Error reading education data: {e}. Using global default.")
        return {}, GLOBAL_DEFAULT

def calculate_school_density_gap():
    parser = argparse.ArgumentParser(description="Calculate school density gap per province.")
    parser.add_argument("--iso3", default="BFA", help="ISO3 country code (default: BFA)")
    args = parser.parse_args()
    
    iso3 = args.iso3.upper()
    iso3_lower = iso3.lower()
    
    print(f"🚀 Calculating School Density Gap for {iso3}...")
    
    # 1. Load Dynamic School-Age Percentages
    pct_lookup, fallback_pct = get_school_age_pct_info(iso3)

    # 2. Find available years from the index
    index_path = f"data/clean/{iso3_lower}_pop_density/{iso3_lower}_index.json"
    if not os.path.exists(index_path):
        print(f"❌ Error: {index_path} not found. Run fetch_worldpop.py first.")
        return

    with open(index_path, "r") as f:
        index_data = json.load(f)

    zonal_files = index_data.get("zonal_files", {})
    if not zonal_files:
        print(f"❌ Error: No zonal files found in {index_path}. Did you use --boundary in fetch_worldpop.py?")
        return

    # 3. Load Schools and Boundaries
    print("  Loading schools and boundaries...")
    schools_gdf = gpd.read_file("artifacts/schools.geojson")
    bounds_gdf = gpd.read_file("data/raw/boundaries/BFA_admin2.geojson")
    
    # Extract area info from boundaries
    province_info = bounds_gdf[["adm2_name", "area_sqkm"]].copy()
    
    if schools_gdf.crs != bounds_gdf.crs:
        schools_gdf = schools_gdf.to_crs(bounds_gdf.crs)
        
    joined = gpd.sjoin(schools_gdf, bounds_gdf, predicate="within")
    school_counts = joined.groupby("adm2_name").size().reset_index(name="school_count")

    all_results = []

    for year_str, filename in zonal_files.items():
        year = int(year_str)
        zonal_path = os.path.join(f"data/clean/{iso3_lower}_pop_density", filename)
        
        print(f"\n--- Processing Year: {year} ---")
        if not os.path.exists(zonal_path):
            print(f"  ⚠️ Skipping: {filename} not found.")
            continue

        pop_df = pd.read_csv(zonal_path)
        
        # Apply dynamic percentage
        if year in pct_lookup:
            pct = pct_lookup[year]
            source = "Master Education (Yearly)"
        else:
            pct = fallback_pct
            source = "Country/Global Average"
            
        print(f"  Using school-age factor: {pct:.2%} (Source: {source})")
        
        pop_df["school_age_pop"] = pop_df["Population"] * pct
        
        # Merge with school counts and province area
        merged = pd.merge(
            pop_df, 
            school_counts, 
            left_on="Region", 
            right_on="adm2_name", 
            how="left"
        ).fillna(0)
        
        merged = pd.merge(
            merged,
            province_info,
            left_on="Region",
            right_on="adm2_name",
            how="left"
        ).drop(columns=["adm2_name_y"]).rename(columns={"adm2_name_x": "adm2_name"})

        # --- Core Metrics ---
        
        # 1. Schools per 1,000 children (Standard Density Metric)
        # Avoid div by zero with +1
        merged["schools_per_1000_children"] = (merged["school_count"] / (merged["school_age_pop"] + 1)) * 1000
        
        # 2. Schools per km2 (Spatial Coverage)
        merged["schools_per_km2"] = merged["school_count"] / merged["area_sqkm"]
        
        # 3. Child Population Density (Children per km2)
        merged["child_pop_density"] = merged["school_age_pop"] / merged["area_sqkm"]

        # The "Density Gap" is our primary fragility indicator: 
        # Provinces with high child population but low school count.
        merged["density_gap"] = merged["schools_per_1000_children"]
        merged["year"] = year
        
        all_results.append(merged)

    if not all_results:
        return

    final_df = pd.concat(all_results)
    
    # 4. Invert and Normalize across all processed data
    max_gap = final_df["density_gap"].max()
    min_gap = final_df["density_gap"].min()
    
    if max_gap > min_gap:
        final_df["density_norm"] = (final_df["density_gap"] - min_gap) / (max_gap - min_gap)
    else:
        final_df["density_norm"] = 0
        
    final_df["school_fragility_score"] = 1 - final_df["density_norm"]
    
    # 5. Save results
    output_path = "artifacts/province_school_fragility.csv"
    final_df.to_csv(output_path, index=False)
    print(f"\n✅ Saved school fragility scores to {output_path}")
    
    # Show Top 5 Most Fragile for the latest year
    latest_year = max(int(y) for y in zonal_files.keys())
    print(f"\nTop 5 Most Fragile Provinces in {latest_year}:")
    top_5 = final_df[final_df["year"] == latest_year].sort_values("school_fragility_score", ascending=False)
    print(top_5[["Region", "school_count", "school_age_pop", "school_fragility_score"]].head())

if __name__ == "__main__":
    calculate_school_density_gap()
