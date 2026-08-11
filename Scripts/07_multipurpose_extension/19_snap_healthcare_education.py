"""
Script 19: Snap hospital/school/university points to the walk graph.

Same snapping technique as script 11 (Small Area centroids) and script 08
(GTFS stops).

INPUT:
    data/raw/osm/{hospitals,schools,universities}.csv
    data/processed/network_graph/walk_graph.pickle

OUTPUT:
    data/processed/accessibility_scores/{hospitals,schools,universities}_snapped.csv

Run from the project root:
    python scripts/07_multipurpose_extension/19_snap_healthcare_education.py
"""
import pandas as pd
import pickle
import numpy as np
from pathlib import Path
from sklearn.neighbors import BallTree

OSM_DIR = Path("data/raw/osm")
GRAPH_DIR = Path("data/processed/network_graph")
ACC_DIR = Path("data/processed/accessibility_scores")
ACC_DIR.mkdir(parents=True, exist_ok=True)

EARTH_RADIUS_M = 6_371_000
FACILITY_FILES = ["hospitals.csv", "schools.csv", "universities.csv"]


def main():
    print("Loading walk graph...")
    with open(GRAPH_DIR / "walk_graph.pickle", "rb") as f:
        G = pickle.load(f)
    node_ids = list(G.nodes())
    node_coords = np.array([[G.nodes[n]["y"], G.nodes[n]["x"]] for n in node_ids])
    tree = BallTree(np.radians(node_coords), metric="haversine")
    print(f"Walk graph nodes: {len(node_ids)}")

    for fname in FACILITY_FILES:
        path = OSM_DIR / fname
        if not path.exists():
            print(f"WARNING: {path} not found, skipping (run script 18 first)")
            continue

        df = pd.read_csv(path)
        print(f"\n{fname}: {len(df)} points")

        coords_rad = np.radians(df[["lat", "lon"]].values)
        distances_rad, indices = tree.query(coords_rad, k=1)
        df["walk_node_id"] = [node_ids[i] for i in indices.flatten()]
        df["snap_distance_m"] = distances_rad.flatten() * EARTH_RADIUS_M

        out_name = fname.replace(".csv", "_snapped.csv")
        df.to_csv(ACC_DIR / out_name, index=False)
        print(f"  Median snap distance: {df.snap_distance_m.median():.1f}m")
        print(f"  Max snap distance: {df.snap_distance_m.max():.1f}m")
        print(f"  Saved {out_name}")


if __name__ == "__main__":
    main()
