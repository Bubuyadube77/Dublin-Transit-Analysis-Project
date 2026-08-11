"""
Script 07: Build transit edges (stop-to-stop travel times) and compute
headways / expected wait times by time-of-day period.

Time periods (reasonable default, adjustable later):
    AM_PEAK   : 07:00 - 09:30
    PM_PEAK   : 16:00 - 18:30
    OFF_PEAK  : everything else within service hours

We analyze a single representative weekday (Wednesday) rather than every
service pattern, to keep "typical weekday service" well-defined and avoid
double-counting variants (school-day-only trips, etc).

INPUT: data/raw/gtfs/{stop_times,trips,calendar}.txt
OUTPUT:
    data/processed/network_graph/transit_edges.csv
        from_stop, to_stop, route_id, trip_id, travel_time_seconds
    data/processed/network_graph/stop_headways.csv
        stop_id, period, headway_seconds, wait_time_seconds, num_departures

Run from the project root:
    python scripts/02_network_construction/07_build_transit_edges.py
"""
import pandas as pd
from pathlib import Path

GTFS_DIR = Path("data/raw/gtfs")
OUT_DIR = Path("data/processed/network_graph")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Time period windows, in seconds-since-midnight
PERIODS = {
    "AM_PEAK": (7 * 3600, 9.5 * 3600),
    "PM_PEAK": (16 * 3600, 18.5 * 3600),
    # OFF_PEAK covers the rest of the 05:00-24:00 service day, split into
    # two windows since AM/PM peak sit in the middle of it
    "OFF_PEAK_1": (5 * 3600, 7 * 3600),
    "OFF_PEAK_2": (9.5 * 3600, 16 * 3600),
    "OFF_PEAK_3": (18.5 * 3600, 24 * 3600),
}

REPRESENTATIVE_DAY = "wednesday"  # column name in calendar.txt


def time_to_seconds(t):
    """Convert GTFS HH:MM:SS (hours can exceed 24) to seconds since midnight."""
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def classify_period(seconds):
    for period, (start, end) in PERIODS.items():
        if start <= seconds < end:
            return period
    return None  # outside 05:00-24:00, e.g. very early/late night trips


def main():
    print("Loading GTFS files...")
    stop_times = pd.read_csv(GTFS_DIR / "stop_times.txt")
    trips = pd.read_csv(GTFS_DIR / "trips.txt")
    calendar = pd.read_csv(GTFS_DIR / "calendar.txt")

    # Pick service_ids that run on our representative weekday
    weekday_service_ids = set(
        calendar.loc[calendar[REPRESENTATIVE_DAY] == 1, "service_id"].astype(str)
    )
    print(f"Service patterns active on a {REPRESENTATIVE_DAY}: {len(weekday_service_ids)}")

    weekday_trips = trips[trips.service_id.astype(str).isin(weekday_service_ids)]
    weekday_trip_ids = set(weekday_trips.trip_id.astype(str))
    print(f"Trips running on a representative weekday: {len(weekday_trip_ids)}")

    st = stop_times[stop_times.trip_id.astype(str).isin(weekday_trip_ids)].copy()
    print(f"stop_times rows for representative weekday: {len(st)}")

    print("Converting times to seconds...")
    st["dep_sec"] = st["departure_time"].apply(time_to_seconds)
    st["arr_sec"] = st["arrival_time"].apply(time_to_seconds)

    # --- Build stop-to-stop edges ---
    print("Building stop-to-stop transit edges...")
    st_sorted = st.sort_values(["trip_id", "stop_sequence"])
    st_sorted["next_stop_id"] = st_sorted.groupby("trip_id")["stop_id"].shift(-1)
    st_sorted["next_arr_sec"] = st_sorted.groupby("trip_id")["arr_sec"].shift(-1)

    edges = st_sorted.dropna(subset=["next_stop_id"]).copy()
    edges["travel_time_seconds"] = edges["next_arr_sec"] - edges["dep_sec"]
    edges = edges[edges["travel_time_seconds"] > 0]  # drop bad/overnight-wrap rows

    edges = edges.merge(
        weekday_trips[["trip_id", "route_id"]], on="trip_id", how="left"
    )

    edges_out = edges[
        ["stop_id", "next_stop_id", "route_id", "trip_id", "travel_time_seconds"]
    ].rename(columns={"stop_id": "from_stop", "next_stop_id": "to_stop"})

    edges_out.to_csv(OUT_DIR / "transit_edges.csv", index=False)
    print(f"Saved {len(edges_out)} transit edges")

    # --- Compute headways / wait times per stop per period ---
    print("Computing headways by time period...")
    st["period"] = st["dep_sec"].apply(classify_period)
    st_valid = st.dropna(subset=["period"])

    records = []
    for (stop_id, period), group in st_valid.groupby(["stop_id", "period"]):
        n_departures = len(group)
        window_start, window_end = PERIODS[period]
        window_duration = window_end - window_start

        if n_departures >= 2:
            departures_sorted = group["dep_sec"].sort_values().values
            gaps = departures_sorted[1:] - departures_sorted[:-1]
            headway = gaps.mean()
        elif n_departures == 1:
            # Only one departure in the window -- treat headway as the
            # full window duration (conservative: you might just miss it)
            headway = window_duration
        else:
            headway = None

        wait_time = headway / 2 if headway is not None else None

        records.append({
            "stop_id": stop_id,
            "period": period,
            "num_departures": n_departures,
            "headway_seconds": headway,
            "wait_time_seconds": wait_time,
        })

    headways_df = pd.DataFrame(records)
    headways_df.to_csv(OUT_DIR / "stop_headways.csv", index=False)
    print(f"Saved headways for {headways_df.stop_id.nunique()} stops across {len(PERIODS)} periods")

    print("\nSample headways (AM_PEAK):")
    print(headways_df[headways_df.period == "AM_PEAK"].sort_values("headway_seconds").head(10))


if __name__ == "__main__":
    main()
