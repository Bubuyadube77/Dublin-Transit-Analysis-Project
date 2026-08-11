"""
Script 12: Compute travel time from every Small Area centroid to every
employment destination, using efficient reverse-Dijkstra.

Rather than running one shortest-path search per Small Area (5,076 separate
searches across a ~940K node graph -- far too slow), we run the search
BACKWARDS from each of the small number of destinations instead. This is
mathematically equivalent (same travel times) but only requires one search
per destination (6 total), each of which computes distances to every other
node in the graph in a single pass.

INPUT:
    data/processed/network_graph/multimodal_graph.pickle
    data/processed/accessibility_scores/small_area_centroids.csv
    data/processed/accessibility_scores/employment_destinations_snapped.csv

OUTPUT:
    data/processed/accessibility_scores/accessibility_scores.csv
        SA_PUB2022, and one column per destination with travel time in
        minutes, plus min_travel_time_min (nearest employment cluster)

Run from the project root:
    python scripts/03_accessibility_computation/12_compute_accessibility.py
"""
import pandas as pd
import pickle
import networkx as nx
import time
from pathlib import Path

GRAPH_DIR = Path("data/processed/network_graph")
ACC_DIR = Path("data/processed/accessibility_scores")

UNREACHABLE_MINUTES = 999  # sentinel value for centroids with no path found


def main():
    print("Loading multimodal graph...")
    with open(GRAPH_DIR / "multimodal_graph.pickle", "rb") as f:
        G = pickle.load(f)
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    print("Building reversed graph for backward search...")
    G_rev = G.reverse(copy=False)

    centroids = pd.read_csv(ACC_DIR / "small_area_centroids.csv")
    destinations = pd.read_csv(ACC_DIR / "employment_destinations_snapped.csv")
    print(f"\nSmall Areas: {len(centroids)}")
    print(f"Destinations: {len(destinations)}")

    results = centroids[["SA_PUB2022", "walk_node_id"]].copy()

    for _, dest_row in destinations.iterrows():
        dest_name = dest_row["name"]
        dest_node = dest_row["walk_node_id"]
        col_name = dest_name.replace(" ", "_").replace("/", "_")

        print(f"\nComputing travel times to: {dest_name}...")
        t0 = time.time()

        # Single-source Dijkstra on the REVERSED graph, starting at the
        # destination, gives shortest travel time FROM every node TO the
        # destination in the original graph.
        try:
            travel_times = nx.single_source_dijkstra_path_length(
                G_rev, dest_node, weight="travel_time"
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            travel_times = {}

        print(f"  Reached {len(travel_times)} nodes in {time.time()-t0:.1f}s")

        results[f"{col_name}_min"] = results["walk_node_id"].map(
            lambda n: travel_times.get(n, None)
        )
        results[f"{col_name}_min"] = results[f"{col_name}_min"] / 60.0

        n_unreachable = results[f"{col_name}_min"].isna().sum()
        print(f"  Small Areas with NO path to this destination: {n_unreachable}")

    # Compute the nearest-employment-cluster accessibility metric.
    # Some Small Areas may have no path to ANY destination (isolated from
    # the main graph component) -- idxmin errors on all-NaN rows, so we
    # guard for that explicitly.
    dest_cols = [c for c in results.columns if c.endswith("_min")]
    results["min_travel_time_min"] = results[dest_cols].min(axis=1)

    def safe_idxmin(row):
        if row.isna().all():
            return None
        return row.idxmin()

    results["nearest_destination"] = results[dest_cols].apply(safe_idxmin, axis=1)

    n_fully_unreachable = results["min_travel_time_min"].isna().sum()
    print(f"\nSmall Areas unreachable from ALL destinations: {n_fully_unreachable}")

    results.to_csv(ACC_DIR / "accessibility_scores.csv", index=False)
    print(f"\nSaved accessibility_scores.csv")

    print("\nSummary of minimum travel time to nearest employment cluster:")
    print(results["min_travel_time_min"].describe())


if __name__ == "__main__":
    main()
