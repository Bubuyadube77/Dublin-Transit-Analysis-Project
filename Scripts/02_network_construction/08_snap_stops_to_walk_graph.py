"""
Script 08: Snap each GTFS stop to its nearest node in the walk network graph.

This creates the "how do you actually reach the bus stop from the street
network" linkage that connects the transit layer to the walk layer.

INPUT:
    data/raw/gtfs/stops.txt
    data/processed/network_graph/walk_graph.pickle

OUTPUT:
    data/processed/network_graph/stop_to_walk_node.csv
        stop_id, walk_node_id, snap_distance_m

Run from the project root:
    python scripts/02_network_construction/08_snap_stops_to_walk_graph.py
"""
import pandas as pd
import pickle
import numpy as np
from pathlib import Path
from sklearn.neighbors import BallTree

GTFS_DIR = Path("data/raw/gtfs")
GRAPH_DIR = Path("data/processed/network_graph")

EARTH_RADIUS_M = 6_371_000
MAX_SNAP_DISTANCE_M = 300  # stops beyond this from any walk node are flagged


def main():
    print("Loading walk graph...")
    with open(GRAPH_DIR / "walk_graph.pickle", "rb") as f:
        G = pickle.load(f)

    node_ids = list(G.nodes())
    node_coords = np.array([[G.nodes[n]["y"], G.nodes[n]["x"]] for n in node_ids])  # lat, lon
    node_coords_rad = np.radians(node_coords)

    print(f"Walk graph nodes: {len(node_ids)}")
    print("Building BallTree for nearest-neighbor search...")
    tree = BallTree(node_coords_rad, metric="haversine")

    print("Loading GTFS stops...")
    stops = pd.read_csv(GTFS_DIR / "stops.txt")
    print(f"Stops: {len(stops)}")

    stop_coords_rad = np.radians(stops[["stop_lat", "stop_lon"]].values)

    print("Finding nearest walk node for each stop...")
    distances_rad, indices = tree.query(stop_coords_rad, k=1)
    distances_m = distances_rad.flatten() * EARTH_RADIUS_M

    results = pd.DataFrame({
        "stop_id": stops["stop_id"].values,
        "walk_node_id": [node_ids[i] for i in indices.flatten()],
        "snap_distance_m": distances_m,
    })

    results.to_csv(GRAPH_DIR / "stop_to_walk_node.csv", index=False)
    print(f"Saved {len(results)} stop-to-node mappings")

    beyond_threshold = results[results.snap_distance_m > MAX_SNAP_DISTANCE_M]
    print(f"\nStops farther than {MAX_SNAP_DISTANCE_M}m from any walk node: {len(beyond_threshold)}")
    print(f"Median snap distance: {results.snap_distance_m.median():.1f}m")
    print(f"Max snap distance: {results.snap_distance_m.max():.1f}m")

    if len(beyond_threshold) > 0:
        print("\nSample flagged stops (may indicate gaps in OSM walk data near these stops):")
        print(beyond_threshold.sort_values("snap_distance_m", ascending=False).head(10))


if __name__ == "__main__":
    main()
