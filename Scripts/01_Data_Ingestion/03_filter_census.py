"""
Script 03: Filter CSO Census 2022 Small Area data + boundaries to the Dublin Region

INPUT (place these in data/raw/census_national/):
    SAPS_2022_Small_Area_UR_171024.csv
        -- from cso.ie Census 2022 Small Area Population Statistics page
    SMALL_AREA_2022_...gpkg
        -- the GeoPackage (NOT the CSV) version of the Small Area boundaries,
           downloaded from the Tailte Eireann / GeoHive open data portal.
           Must contain actual polygon geometry, not just attributes.

OUTPUT:
    data/raw/census/dublin_small_area_saps.csv
    data/processed/boundaries/dublin_small_areas_itm.gpkg   (EPSG:2157)
    data/processed/boundaries/dublin_small_areas_wgs84.gpkg (EPSG:4326)

Run from the project root:
    python scripts/01_data_ingestion/03_filter_census.py
"""
import pandas as pd
import geopandas as gpd
from pathlib import Path

RAW_NATIONAL = Path("data/raw/census_national")
CENSUS_OUT = Path("data/raw/census")
BOUNDARY_OUT = Path("data/processed/boundaries")
CENSUS_OUT.mkdir(parents=True, exist_ok=True)
BOUNDARY_OUT.mkdir(parents=True, exist_ok=True)

DUBLIN_COUNTIES = {"DUBLIN CITY", "FINGAL", "SOUTH DUBLIN", "DUN LAOGHAIRE/RATHDOWN"}

# CHANGE THIS to match your actual downloaded boundary geopackage filename
BOUNDARY_GPKG_NAME = "SMALL_AREA_2022_boundaries.gpkg"


def main():
    print("Loading Small Area boundary geopackage (has real geometry)...")
    gdf = gpd.read_file(RAW_NATIONAL / BOUNDARY_GPKG_NAME)
    print(f"National Small Areas: {len(gdf)}")
    print("Columns:", list(gdf.columns))

    gda_gdf = gdf[gdf.COUNTY_ENGLISH.isin(DUBLIN_COUNTIES)].copy()
    print(f"Dublin Region Small Areas: {len(gda_gdf)}")
    print(gda_gdf.COUNTY_ENGLISH.value_counts())

    gda_sa_ids = set(gda_gdf.SA_PUB2022.astype(str))

    print("\nLoading SAPS population/socioeconomic data...")
    saps = pd.read_csv(RAW_NATIONAL / "SAPS_2022_Small_Area_UR_171024.csv")
    print(f"National SAPS rows: {len(saps)}")

    saps["GEOGID_str"] = saps["GEOGID"].astype(str)
    gda_saps = saps[saps.GEOGID_str.isin(gda_sa_ids)].drop(columns=["GEOGID_str"])
    print(f"Dublin Region SAPS rows matched: {len(gda_saps)}")

    missing = gda_sa_ids - set(saps.GEOGID.astype(str))
    print(f"Boundaries with NO matching SAPS row: {len(missing)}")

    # Save population/socioeconomic data
    gda_saps.to_csv(CENSUS_OUT / "dublin_small_area_saps.csv", index=False)

    # Save boundaries in both CRS -- ITM for accurate area calc, WGS84 for
    # overlaying with GTFS stop coordinates later
    print(f"\nBoundary CRS: {gda_gdf.crs}")
    gda_gdf.to_file(BOUNDARY_OUT / "dublin_small_areas_itm.gpkg", driver="GPKG")
    gda_gdf_wgs84 = gda_gdf.to_crs(epsg=4326)
    gda_gdf_wgs84.to_file(BOUNDARY_OUT / "dublin_small_areas_wgs84.gpkg", driver="GPKG")

    print(f"\nTotal Dublin Region area (km2): {gda_gdf.geometry.area.sum() / 1_000_000:.1f}")
    print("Done.")

    # Report car-ownership columns available for the equity variable
    car_cols = [c for c in saps.columns if "T15_1" in c]
    print(f"\nCar-ownership columns available (Theme 15): {car_cols}")


if __name__ == "__main__":
    main()
