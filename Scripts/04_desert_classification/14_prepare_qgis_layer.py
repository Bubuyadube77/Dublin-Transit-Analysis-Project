"""
Script 14: Prepare the final QGIS-ready spatial layer.

Joins the transit desert classification (script 13, currently a flat CSV)
back to the actual Small Area polygon geometry, so it can be opened
directly in QGIS and mapped.

INPUT:
    data/processed/accessibility_scores/transit_desert_classification.csv
    data/processed/boundaries/dublin_small_areas_wgs84.gpkg

OUTPUT:
    outputs/maps/qgis_project/dublin_transit_deserts.gpkg
        (one layer, ready to drag into QGIS)

Run from the project root:
    python scripts/04_desert_classification/14_prepare_qgis_layer.py
"""
import pandas as pd
import geopandas as gpd
from pathlib import Path

CLASSIFICATION_FILE = Path("data/processed/accessibility_scores/transit_desert_classification.csv")
BOUNDARY_FILE = Path("data/processed/boundaries/dublin_small_areas_wgs84.gpkg")
OUT_DIR = Path("outputs/maps/qgis_project")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("Loading classification results...")
    classification = pd.read_csv(CLASSIFICATION_FILE)
    print(f"Classified Small Areas: {len(classification)}")

    print("Loading boundary geometry...")
    boundary = gpd.read_file(BOUNDARY_FILE)
    print(f"Total Dublin Small Areas (incl. unclassifiable ones): {len(boundary)}")

    # Left join FROM boundary so every Small Area still appears on the map
    # even if it couldn't be classified (shows as null/no-data, rather than
    # silently vanishing -- important so the map doesn't look like there
    # are gaps in Dublin itself)
    cols_to_keep = [
        "SA_PUB2022", "no_car_rate", "min_travel_time_min", "nearest_destination",
        "need_percentile", "access_percentile", "quadrant", "desert_severity_index",
        "ed_deprivation_score", "ed_deprivation_category",
    ]
    merged = boundary.merge(
        classification[cols_to_keep], on="SA_PUB2022", how="left"
    )

    merged["quadrant"] = merged["quadrant"].fillna("No data (unreachable/missing)")

    print(f"\nFinal merged layer: {len(merged)} features")
    print("Quadrant breakdown (including unclassified):")
    print(merged["quadrant"].value_counts())

    out_path = OUT_DIR / "dublin_transit_deserts.gpkg"
    merged.to_file(out_path, driver="GPKG", layer="transit_deserts")
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()
