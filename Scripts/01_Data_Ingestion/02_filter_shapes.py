"""
Script 02: Filter shapes.txt to only the shape_ids used by GDA trips (optional)

Run script 01 first -- it produces data/raw/gtfs/gda_shape_ids.txt, which
this script depends on.

INPUT: data/raw/gtfs_national/shapes.txt
OUTPUT: data/raw/gtfs/shapes.txt

Run from the project root:
    python scripts/01_data_ingestion/02_filter_shapes.py
"""
import pandas as pd
from pathlib import Path

RAW_NATIONAL = Path("data/raw/gtfs_national")
OUT_DIR = Path("data/raw/gtfs")

SHAPE_IDS_FILE = OUT_DIR / "gda_shape_ids.txt"


def main():
    if not SHAPE_IDS_FILE.exists():
        print(f"ERROR: {SHAPE_IDS_FILE} not found. Run 01_filter_gtfs.py first.")
        return

    with open(SHAPE_IDS_FILE) as f:
        gda_shape_ids = set(line.strip() for line in f if line.strip())
    print(f"Target shape_ids: {len(gda_shape_ids)}")

    print("Loading national shapes.txt (large file)...")
    shapes = pd.read_csv(RAW_NATIONAL / "shapes.txt")
    print(f"National shape points: {len(shapes)}")

    gda_shapes = shapes[shapes.shape_id.astype(str).isin(gda_shape_ids)]
    print(f"Filtered shape points: {len(gda_shapes)}")

    gda_shapes.to_csv(OUT_DIR / "shapes.txt", index=False)
    print("Saved data/raw/gtfs/shapes.txt")


if __name__ == "__main__":
    main()
