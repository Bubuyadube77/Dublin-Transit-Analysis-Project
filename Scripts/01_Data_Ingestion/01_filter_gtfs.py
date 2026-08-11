"""
Script 01: Filter national GTFS feed to the Greater Dublin Area (GDA)

INPUT (place these in data/raw/gtfs_national/):
    stops.txt, stop_times.txt, trips.txt, routes.txt, agency.txt, calendar.txt
    (downloaded from the Mobility Database TFI feed)

OUTPUT (written to data/raw/gtfs/):
    Same filenames, filtered to stops within the GDA bounding box and
    everything that references those stops.

Run from the project root:
    python scripts/01_data_ingestion/01_filter_gtfs.py
"""
import pandas as pd
from pathlib import Path

RAW_NATIONAL = Path("data/raw/gtfs_national")
OUT_DIR = Path("data/raw/gtfs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Greater Dublin Area bounding box
LAT_MIN, LAT_MAX = 53.15, 53.65
LON_MIN, LON_MAX = -6.55, -6.00


def main():
    print("Loading stops...")
    stops = pd.read_csv(RAW_NATIONAL / "stops.txt")
    print(f"National stops: {len(stops)}")

    gda_stops = stops[
        stops.stop_lat.between(LAT_MIN, LAT_MAX)
        & stops.stop_lon.between(LON_MIN, LON_MAX)
    ].copy()
    print(f"GDA stops: {len(gda_stops)}")
    gda_stop_ids = set(gda_stops.stop_id.astype(str))

    print("Loading stop_times.txt (large file, may take a minute)...")
    chunks = []
    for chunk in pd.read_csv(RAW_NATIONAL / "stop_times.txt", chunksize=500_000):
        filtered = chunk[chunk.stop_id.astype(str).isin(gda_stop_ids)]
        if len(filtered) > 0:
            chunks.append(filtered)
    gda_stop_times = pd.concat(chunks, ignore_index=True)
    print(f"GDA stop_times rows: {len(gda_stop_times)}")

    gda_trip_ids = set(gda_stop_times.trip_id.astype(str))
    print(f"GDA trip ids: {len(gda_trip_ids)}")

    print("Loading trips.txt...")
    trips = pd.read_csv(RAW_NATIONAL / "trips.txt")
    gda_trips = trips[trips.trip_id.astype(str).isin(gda_trip_ids)]
    print(f"GDA trips: {len(gda_trips)}")

    gda_route_ids = set(gda_trips.route_id.astype(str))
    gda_service_ids = set(gda_trips.service_id.astype(str))

    print("Loading routes.txt...")
    routes = pd.read_csv(RAW_NATIONAL / "routes.txt")
    gda_routes = routes[routes.route_id.astype(str).isin(gda_route_ids)]
    print(f"GDA routes: {len(gda_routes)}")
    print("route_type breakdown:")
    print(gda_routes.route_type.value_counts())

    gda_agency_ids = set(gda_routes.agency_id.astype(str))

    print("Loading agency.txt and calendar.txt...")
    agency = pd.read_csv(RAW_NATIONAL / "agency.txt")
    gda_agency = agency[agency.agency_id.astype(str).isin(gda_agency_ids)]

    calendar = pd.read_csv(RAW_NATIONAL / "calendar.txt")
    gda_calendar = calendar[calendar.service_id.astype(str).isin(gda_service_ids)]
    print(f"GDA calendar entries: {len(gda_calendar)}")

    # Save everything
    gda_stops.to_csv(OUT_DIR / "stops.txt", index=False)
    gda_stop_times.to_csv(OUT_DIR / "stop_times.txt", index=False)
    gda_trips.to_csv(OUT_DIR / "trips.txt", index=False)
    gda_routes.to_csv(OUT_DIR / "routes.txt", index=False)
    gda_agency.to_csv(OUT_DIR / "agency.txt", index=False)
    gda_calendar.to_csv(OUT_DIR / "calendar.txt", index=False)

    # Save shape_ids needed, in case shapes.txt is filtered separately (script 02)
    if "shape_id" in gda_trips.columns:
        shape_ids = gda_trips["shape_id"].dropna().astype(str).unique()
        with open(OUT_DIR / "gda_shape_ids.txt", "w") as f:
            f.write("\n".join(shape_ids))
        print(f"Saved {len(shape_ids)} needed shape_ids to gda_shape_ids.txt")

    print("\nDone. Filtered GTFS written to", OUT_DIR)
    print("\nAgencies serving GDA:")
    print(gda_agency[["agency_id", "agency_name"]].to_string(index=False))


if __name__ == "__main__":
    main()
