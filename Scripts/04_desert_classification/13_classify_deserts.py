"""
Script 13: Transit desert classification (Stage D)

Implements the formal demand-supply mismatch framework (Jiao & Dillivan)
rather than treating "low accessibility" alone as a desert -- an area with
poor transit access where most households own cars isn't really a policy
priority; an area with poor access AND high car-dependency-by-necessity is.

Method:
    1. NEED score = no-car-ownership rate per Small Area (Census 2022, T15)
    2. ACCESS score = travel time to nearest employment cluster (Stage C)
    3. Percentile-rank both across all Dublin Small Areas
    4. Classify into a 2x2 quadrant using the median split on each axis:
        - High need + Low access  -> TRANSIT DESERT (priority zone)
        - High need + High access -> Well-served, high-need
        - Low need  + Low access  -> Low-priority gap
        - Low need  + High access -> Well-served, low-need
    5. Continuous DESERT SEVERITY INDEX = need_percentile - access_percentile
       (ranges roughly -1 to +1; higher = more desert-like)

Also attaches the Pobal ED-level deprivation score for each Small Area's
parent ED, purely for cross-comparison against Ahern et al.'s original
deprivation-based framework -- NOT used in the primary classification,
since deprivation is only available at the coarser ED level.

INPUT:
    data/processed/accessibility_scores/accessibility_scores.csv
    data/raw/census/dublin_small_area_saps.csv
    data/raw/deprivation_index/dublin_ed_deprivation_2022.csv
    data/processed/boundaries/dublin_small_areas_wgs84.gpkg (for ED crosswalk)

OUTPUT:
    data/processed/accessibility_scores/transit_desert_classification.csv

Run from the project root:
    python scripts/04_desert_classification/13_classify_deserts.py
"""
import pandas as pd
import geopandas as gpd
from pathlib import Path

ACC_DIR = Path("data/processed/accessibility_scores")
CENSUS_FILE = Path("data/raw/census/dublin_small_area_saps.csv")
DEPRIVATION_FILE = Path("data/raw/deprivation_index/dublin_ed_deprivation_2022.csv")
BOUNDARY_FILE = Path("data/processed/boundaries/dublin_small_areas_wgs84.gpkg")


def main():
    print("Loading accessibility scores...")
    access = pd.read_csv(ACC_DIR / "accessibility_scores.csv")
    print(f"Small Areas with accessibility data: {len(access)}")

    print("Loading census car-ownership data...")
    census = pd.read_csv(CENSUS_FILE)
    census["no_car_rate"] = census["T15_1_NC"] / census["T15_1_TC"]
    census_slim = census[["GEOGID", "T15_1_NC", "T15_1_TC", "no_car_rate"]].rename(
        columns={"GEOGID": "SA_PUB2022"}
    )

    print("Loading ED crosswalk from boundary file...")
    boundary = gpd.read_file(BOUNDARY_FILE)[["SA_PUB2022", "ED_ID_STR", "ED_ENGLISH", "COUNTY_ENGLISH"]]

    print("Loading Pobal deprivation index (ED level, for comparison only)...")
    deprivation = pd.read_csv(DEPRIVATION_FILE)
    deprivation_slim = deprivation[
        ["ED_ID_STR", "Index22_ED_std_rel_wt", "Index22_rel_wt_lab"]
    ].rename(columns={
        "Index22_ED_std_rel_wt": "ed_deprivation_score",
        "Index22_rel_wt_lab": "ed_deprivation_category",
    })

    # Merge everything together
    df = access.merge(census_slim, on="SA_PUB2022", how="left")
    df = df.merge(boundary, on="SA_PUB2022", how="left")
    df["ED_ID_STR"] = df["ED_ID_STR"].astype(str)
    deprivation_slim["ED_ID_STR"] = deprivation_slim["ED_ID_STR"].astype(str)
    df = df.merge(deprivation_slim, on="ED_ID_STR", how="left")

    print(f"\nMerged dataset: {len(df)} rows")
    print(f"Missing accessibility score: {df.min_travel_time_min.isna().sum()}")
    print(f"Missing no_car_rate: {df.no_car_rate.isna().sum()}")

    # Only classify Small Areas with BOTH a valid access score and a valid
    # need score -- drop the unreachable ones from Stage C plus any census
    # join misses
    classifiable = df.dropna(subset=["min_travel_time_min", "no_car_rate"]).copy()
    print(f"\nClassifiable Small Areas (have both need + access data): {len(classifiable)}")

    # --- Percentile ranking ---
    # need_percentile: higher = more car-dependent-by-necessity (higher need)
    classifiable["need_percentile"] = classifiable["no_car_rate"].rank(pct=True)

    # access_percentile: higher = BETTER access (shorter travel time).
    # rank ascending on travel time, then invert so shorter time = higher percentile
    classifiable["access_percentile"] = 1 - classifiable["min_travel_time_min"].rank(pct=True)

    # --- Quadrant classification (median split) ---
    def classify_quadrant(row):
        high_need = row["need_percentile"] >= 0.5
        high_access = row["access_percentile"] >= 0.5
        if high_need and not high_access:
            return "Transit Desert"
        elif high_need and high_access:
            return "Well-served, high-need"
        elif not high_need and not high_access:
            return "Low-priority gap"
        else:
            return "Well-served, low-need"

    classifiable["quadrant"] = classifiable.apply(classify_quadrant, axis=1)

    # --- Continuous severity index ---
    classifiable["desert_severity_index"] = (
        classifiable["need_percentile"] - classifiable["access_percentile"]
    )

    classifiable.to_csv(ACC_DIR / "transit_desert_classification.csv", index=False)
    print(f"\nSaved transit_desert_classification.csv")

    print("\nQuadrant breakdown:")
    print(classifiable["quadrant"].value_counts())

    print("\nTop 15 most severe transit deserts:")
    top_deserts = classifiable.sort_values("desert_severity_index", ascending=False).head(15)
    print(top_deserts[[
        "SA_PUB2022", "ED_ENGLISH", "COUNTY_ENGLISH", "no_car_rate",
        "min_travel_time_min", "desert_severity_index", "ed_deprivation_category"
    ]].to_string(index=False))

    print("\nDesert count by county:")
    deserts_only = classifiable[classifiable.quadrant == "Transit Desert"]
    print(deserts_only.COUNTY_ENGLISH.value_counts())

    print("\nDesert count by ED deprivation category (cross-check vs equity data):")
    print(deserts_only.ed_deprivation_category.value_counts())


if __name__ == "__main__":
    main()
