"""
Script 04: Filter Pobal HP Deprivation Index (2022) to Dublin Electoral Divisions

Run script 03 first -- this depends on the Dublin boundary file it produces,
which contains the list of Dublin ED_ID_STR codes.

INPUT: data/raw/deprivation_national/hp-deprivation-index-scores-2022.xlsx
OUTPUT: data/raw/deprivation_index/dublin_ed_deprivation_2022.csv

Run from the project root:
    python scripts/01_data_ingestion/04_filter_deprivation.py
"""
import pandas as pd
import geopandas as gpd
from pathlib import Path

RAW_NATIONAL = Path("data/raw/deprivation_national")
OUT_DIR = Path("data/raw/deprivation_index")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BOUNDARY_FILE = Path("data/processed/boundaries/dublin_small_areas_itm.gpkg")


def main():
    if not BOUNDARY_FILE.exists():
        print(f"ERROR: {BOUNDARY_FILE} not found. Run 03_filter_census.py first.")
        return

    print("Getting Dublin ED list from boundary file...")
    gda_sa = gpd.read_file(BOUNDARY_FILE)
    dublin_ed_ids = set(gda_sa["ED_ID_STR"].astype(str).unique())
    print(f"Unique Dublin EDs: {len(dublin_ed_ids)}")

    print("Loading national Pobal deprivation index...")
    dep = pd.read_excel(RAW_NATIONAL / "hp-deprivation-index-scores-2022.xlsx")
    print(f"National EDs: {len(dep)}")

    dep["ED_ID_STR_norm"] = dep["ED_ID_STR"].astype(str)
    gda_dep = dep[dep.ED_ID_STR_norm.isin(dublin_ed_ids)].drop(
        columns=["ED_ID_STR_norm"] + (["Unnamed: 0"] if "Unnamed: 0" in dep.columns else [])
    )
    print(f"Matched Dublin EDs: {len(gda_dep)}")

    missing = dublin_ed_ids - set(dep.ED_ID_STR.astype(str))
    print(f"Dublin EDs with NO match: {len(missing)}")

    gda_dep.to_csv(OUT_DIR / "dublin_ed_deprivation_2022.csv", index=False)
    print("Saved dublin_ed_deprivation_2022.csv")

    print("\nDeprivation category breakdown:")
    print(gda_dep["Index22_rel_wt_lab"].value_counts())


if __name__ == "__main__":
    main()
