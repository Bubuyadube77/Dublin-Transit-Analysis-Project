"""
Script 18: Extract hospital, school, and university/college locations from
the OSM extract (Stage F: multi-purpose accessibility extension).

This is the previously-deferred extension addressing research gap #5
(employment-only focus) -- adding healthcare and education destinations,
which matter more for non-commuting populations (elderly, children,
unemployed) than employment access alone.

INPUT: data/raw/osm/dublin_extract.osm.pbf
       (if you deleted this after Stage A, re-clip it first -- see
       scripts/01_data_ingestion/05_clip_osm.py)
OUTPUT:
    data/raw/osm/hospitals.csv
    data/raw/osm/schools.csv
    data/raw/osm/universities.csv

Run from the project root:
    python scripts/07_multipurpose_extension/18_extract_healthcare_education_pois.py
"""
from pyrosm import OSM
import pandas as pd
from pathlib import Path

INPUT_PBF = Path("data/raw/osm/dublin_extract.osm.pbf")
OUT_DIR = Path("data/raw/osm")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_and_save(osm, filter_dict, out_name, label):
    pois = osm.get_pois(custom_filter=filter_dict)
    if pois is None or len(pois) == 0:
        print(f"WARNING: no {label} found")
        return
    pois = pois[pois.geometry.notna()].copy()
    # Compute centroid in the projected ITM CRS (accurate for polygons like
    # large hospital campuses), then convert back to lat/lon
    pois_itm = pois.set_crs(epsg=4326, allow_override=True).to_crs(epsg=2157)
    centroids_wgs84 = pois_itm.geometry.centroid.to_crs(epsg=4326)
    pois["lon"] = centroids_wgs84.x.values
    pois["lat"] = centroids_wgs84.y.values
    pois_out = pois[["id", "name", "lat", "lon"]].copy()
    pois_out["name"] = pois_out["name"].fillna(f"Unnamed {label}")
    pois_out.to_csv(OUT_DIR / out_name, index=False)
    print(f"{label}: {len(pois_out)} saved to {out_name}")
    return pois_out


def main():
    print("Loading OSM extract...")
    osm = OSM(str(INPUT_PBF))

    print("\nExtracting healthcare and education POIs...")
    extract_and_save(osm, {"amenity": ["hospital"]}, "hospitals.csv", "Hospitals")
    extract_and_save(osm, {"amenity": ["school"]}, "schools.csv", "Schools")
    extract_and_save(osm, {"amenity": ["university", "college"]}, "universities.csv", "Universities/Colleges")

    print("\nDone. Review the CSVs -- OSM data can include duplicates or")
    print("non-operational facilities; spot-check before trusting results.")


if __name__ == "__main__":
    main()
