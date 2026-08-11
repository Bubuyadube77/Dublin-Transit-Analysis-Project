"""
Script 10: Define the employment/CBD destination points used for the
Stage C accessibility analysis (Option A: employment-focused, matching
the scope of Ahern et al. for direct comparability).

Rather than a single CBD point, we use a small, named set of Dublin's
major employment clusters -- this is a common, defensible simplification
used in accessibility studies when granular workplace-location data isn't
openly available (which is the case for Ireland at Small Area level).

IMPORTANT: the coordinates below are reasonable approximations. Before
running the full analysis, spot-check them against Google Maps / OSM and
correct if needed -- accuracy here matters since every downstream result
depends on it.

OUTPUT: data/processed/accessibility_scores/employment_destinations.csv

Run from the project root:
    python scripts/03_accessibility_computation/10_define_destinations.py
"""
import pandas as pd
from pathlib import Path

OUT_DIR = Path("data/processed/accessibility_scores")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# name, lat, lon, description -- VERIFY these coordinates before relying on results
DESTINATIONS = [
    {
        "name": "Dublin City Centre (CBD)",
        "lat": 53.3498, "lon": -6.2603,
        "description": "O'Connell St / core retail & office district",
    },
    {
        "name": "IFSC / Docklands",
        "lat": 53.3478, "lon": -6.2438,
        "description": "International Financial Services Centre, major office employment",
    },
    {
        "name": "Sandyford Business District",
        "lat": 53.2635, "lon": -6.2115,
        "description": "Major south Dublin tech/office cluster",
    },
    {
        "name": "Dublin Airport",
        "lat": 53.4213, "lon": -6.2701,
        "description": "Airport employment zone (aviation, logistics, retail)",
    },
    {
        "name": "Blanchardstown",
        "lat": 53.3865, "lon": -6.3809,
        "description": "West Dublin retail/commercial hub",
    },
    {
        "name": "Tallaght",
        "lat": 53.2859, "lon": -6.3672,
        "description": "South-west Dublin town centre / employment hub",
    },
]


def main():
    df = pd.DataFrame(DESTINATIONS)
    df.to_csv(OUT_DIR / "employment_destinations.csv", index=False)
    print(f"Saved {len(df)} employment destination points")
    print(df[["name", "lat", "lon"]].to_string(index=False))
    print("\nIMPORTANT: verify these coordinates against Google Maps/OSM before")
    print("proceeding -- edit the CSV directly if any need correcting.")


if __name__ == "__main__":
    main()
