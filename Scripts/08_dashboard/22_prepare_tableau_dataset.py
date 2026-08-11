"""
Script 22: Build the master Tableau-ready dataset.

Joins geometry (Small Area boundaries) with every field produced across
the whole pipeline -- employment accessibility, healthcare/education
accessibility, compounding disadvantage, deprivation, and raw census
variables -- into ONE file, so building the Tableau dashboard doesn't
require any further data wrangling inside Tableau itself.

Produces two outputs:
    1. A Shapefile (.shp + supporting files) -- Tableau Desktop/Public can
       connect to this directly as a spatial data source, giving you
       filled maps out of the box.
    2. A flat CSV (no geometry) -- for building charts/tables that don't
       need the map, and as a lighter-weight import option.

INPUT:
    data/processed/boundaries/dublin_small_areas_wgs84.gpkg
    data/processed/accessibility_scores/transit_desert_classification.csv
    data/processed/accessibility_scores/healthcare_education_deserts.csv
    data/raw/census/dublin_small_area_saps.csv

OUTPUT:
    outputs/dashboard/dublin_transit_master.shp (+ .dbf, .shx, .prj, .cpg)
    outputs/dashboard/dublin_transit_master.csv

Run from the project root:
    python scripts/08_dashboard/22_prepare_tableau_dataset.py
"""
import pandas as pd
import geopandas as gpd
from pathlib import Path

BOUNDARY_FILE = Path("data/processed/boundaries/dublin_small_areas_wgs84.gpkg")
EMPLOYMENT_FILE = Path("data/processed/accessibility_scores/transit_desert_classification.csv")
COMPOUNDING_FILE = Path("data/processed/accessibility_scores/healthcare_education_deserts.csv")
CENSUS_FILE = Path("data/raw/census/dublin_small_area_saps.csv")
OUT_DIR = Path("outputs/dashboard")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("Loading boundary geometry...")
    boundary = gpd.read_file(BOUNDARY_FILE)
    print(f"Small Areas: {len(boundary)}")

    print("Loading employment accessibility/classification...")
    employment = pd.read_csv(EMPLOYMENT_FILE)
    employment_cols = [
        "SA_PUB2022", "no_car_rate", "min_travel_time_min", "nearest_destination",
        "need_percentile", "access_percentile", "quadrant", "desert_severity_index",
        "ed_deprivation_score", "ed_deprivation_category", "population",
    ]
    employment_cols = [c for c in employment_cols if c in employment.columns]
    employment_slim = employment[employment_cols].rename(columns={"quadrant": "employment_quadrant"})

    print("Loading healthcare/education compounding data...")
    compounding = pd.read_csv(COMPOUNDING_FILE)
    compounding_cols = [
        "SA_PUB2022", "nearest_hospital_min", "nearest_school_min", "nearest_university_min",
        "hospital_quadrant", "school_quadrant", "university_quadrant", "n_desert_categories",
    ]
    compounding_cols = [c for c in compounding_cols if c in compounding.columns]
    compounding_slim = compounding[compounding_cols]

    print("Loading raw census variables (population, age structure)...")
    census = pd.read_csv(CENSUS_FILE)
    census_cols = ["GEOGID", "T1_1AGETT", "T15_1_NC", "T15_1_TC"]
    census_cols = [c for c in census_cols if c in census.columns]
    census_slim = census[census_cols].rename(columns={"GEOGID": "SA_PUB2022", "T1_1AGETT": "total_population"})

    print("Merging...")
    merged = boundary.merge(employment_slim, on="SA_PUB2022", how="left")
    merged = merged.merge(compounding_slim, on="SA_PUB2022", how="left")
    merged = merged.merge(census_slim, on="SA_PUB2022", how="left", suffixes=("", "_census"))

    # Keep only the columns actually useful for the dashboard -- drop
    # internal GUIDs, Irish-language duplicate names, and NUTS codes we
    # never use, which also sidesteps unpredictable Shapefile truncation.
    keep_cols = [
        "SA_PUB2022", "ED_ENGLISH", "COUNTY_ENGLISH", "geometry",
        "no_car_rate", "min_travel_time_min", "nearest_destination",
        "need_percentile", "access_percentile", "employment_quadrant",
        "desert_severity_index", "ed_deprivation_score", "ed_deprivation_category",
        "nearest_hospital_min", "nearest_school_min", "nearest_university_min",
        "hospital_quadrant", "school_quadrant", "university_quadrant",
        "n_desert_categories", "total_population", "T15_1_NC", "T15_1_TC",
    ]
    keep_cols = [c for c in keep_cols if c in merged.columns]
    merged = merged[keep_cols]

    # Fill categorical fields for areas with no data, so Tableau doesn't show blanks
    for col in ["employment_quadrant", "hospital_quadrant", "school_quadrant", "university_quadrant"]:
        if col in merged.columns:
            merged[col] = merged[col].fillna("No data")

    print(f"\nFinal merged dataset: {len(merged)} rows, {len(merged.columns)} columns")
    print("Columns:", list(merged.columns))

    # --- Save as Shapefile (Tableau's most reliable spatial import format) ---
    # Shapefile field names are limited to 10 characters -- rename long
    # columns to fit, and keep a lookup table so the CSV (unrestricted)
    # remains human-readable.
    shp_rename = {
        "min_travel_time_min": "min_tt_min",
        "nearest_destination": "near_dest",
        "need_percentile": "need_pct",
        "access_percentile": "acc_pct",
        "employment_quadrant": "emp_quad",
        "desert_severity_index": "sev_idx",
        "ed_deprivation_score": "dep_score",
        "ed_deprivation_category": "dep_cat",
        "nearest_hospital_min": "hosp_min",
        "nearest_school_min": "sch_min",
        "nearest_university_min": "univ_min",
        "hospital_quadrant": "hosp_quad",
        "school_quadrant": "sch_quad",
        "university_quadrant": "univ_quad",
        "n_desert_categories": "n_desert",
        "total_population": "pop",
        "COUNTY_ENGLISH": "county",
        "ED_ENGLISH": "ed_name",
        "no_car_rate": "no_car_rt",
        "T15_1_NC": "hh_no_car",
        "T15_1_TC": "hh_total",
    }
    unmapped_long = [c for c in merged.columns if c not in shp_rename and len(c) > 10 and c != "geometry"]
    if unmapped_long:
        print(f"WARNING: columns >10 chars still unmapped, will be auto-truncated: {unmapped_long}")
    merged_shp = merged.rename(columns={k: v for k, v in shp_rename.items() if k in merged.columns})
    shp_path = OUT_DIR / "dublin_transit_master.shp"
    merged_shp.to_file(shp_path, driver="ESRI Shapefile")
    print(f"\nSaved Shapefile: {shp_path}")

    # --- Save flat CSV (full column names, no geometry) ---
    csv_df = merged.drop(columns=["geometry"])
    csv_path = OUT_DIR / "dublin_transit_master.csv"
    csv_df.to_csv(csv_path, index=False)
    print(f"Saved CSV: {csv_path}")

    # Save the field name lookup for reference when building the dashboard
    lookup_path = OUT_DIR / "shapefile_field_name_lookup.csv"
    pd.DataFrame(list(shp_rename.items()), columns=["full_name", "shapefile_name"]).to_csv(lookup_path, index=False)
    print(f"Saved field name lookup: {lookup_path}")


if __name__ == "__main__":
    main()
