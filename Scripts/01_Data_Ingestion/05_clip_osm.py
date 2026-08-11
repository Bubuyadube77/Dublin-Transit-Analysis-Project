"""
Script 05: Clip the national OSM .pbf file down to the Greater Dublin Area

This is a thin Python wrapper around the `osmium` command-line tool, which
must be installed separately first (it is NOT a pip package):

    Windows : easiest via WSL (Windows Subsystem for Linux), then
              `sudo apt install osmium-tool` inside WSL
    Mac     : brew install osmium-tool
    Linux   : sudo apt install osmium-tool

If your machine has plenty of RAM (16GB+), you can actually SKIP this
clipping step entirely and just point script 06 directly at the full
national .pbf -- pyrosm can handle it in one shot given enough memory.
This clip step exists only to keep memory usage low.

INPUT: data/raw/osm_national/ireland-and-northern-ireland-latest.osm.pbf
       (from download.geofabrik.de/europe/ireland-and-northern-ireland.html)
OUTPUT: data/raw/osm/dublin_extract.osm.pbf

Run from the project root:
    python scripts/01_data_ingestion/05_clip_osm.py
"""
import subprocess
from pathlib import Path

RAW_NATIONAL = Path("data/raw/osm_national")
OUT_DIR = Path("data/raw/osm")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# CHANGE THIS to match your actual downloaded filename
INPUT_PBF = RAW_NATIONAL / "ireland-and-northern-ireland-latest.osm.pbf"
OUTPUT_PBF = OUT_DIR / "dublin_extract.osm.pbf"

# Greater Dublin Area bounding box: lon_min,lat_min,lon_max,lat_max
BBOX = "-6.5569,53.1682,-5.9863,53.6447"


def main():
    if not INPUT_PBF.exists():
        print(f"ERROR: {INPUT_PBF} not found. Check the filename matches your download.")
        return

    cmd = [
        "osmium", "extract",
        "-b", BBOX,
        "-s", "simple",  # lightweight strategy, low memory use
        str(INPUT_PBF),
        "-o", str(OUTPUT_PBF),
        "--overwrite",
    ]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

    if result.returncode == 0 and OUTPUT_PBF.exists():
        size_mb = OUTPUT_PBF.stat().st_size / 1_000_000
        print(f"\nSuccess: {OUTPUT_PBF} ({size_mb:.1f} MB)")
    else:
        print("\nFAILED. Check that osmium-tool is installed and on your PATH.")


if __name__ == "__main__":
    main()
