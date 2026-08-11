"""
Script 20: Compute travel time from every Small Area to the NEAREST
hospital, NEAREST school, and NEAREST university/college.

Uses multi-source Dijkstra on the reversed graph: rather than searching
from each individual facility separately and taking the minimum (which
would mean 62 + 693 + 136 = 891 separate searches), a single multi-source
search per category finds "distance to the nearest facility in this set"
directly in one pass. This is the same reverse-graph trick as script 12,
extended to handle many destinations per category at once.

INPUT:
    data/processed/network_graph/multimodal_graph.pickle
    data/processed/accessibility_scores/small_area_centroids.csv
    data/processed/accessibility_scores/{hospitals,schools,universities}_snapped.csv

OUTPUT:
    data/processed/accessibility_scores/healthcare_education_accessibility.csv
        SA_PUB2022, nearest_hospital_min, nearest_school_min, nearest_university_min

Run from the project root:
    python scripts/07_multipurpose_extension/20_compute_healthcare_education_access.py
"""
import pandas as pd
import pickle
import networkx as nx
import time
from pathlib import Path

GRAPH_DIR = Path("data/processed/network_graph")
ACC_DIR = Path("data/processed/accessibility_scores")

CATEGORIES = {
    "hospital": "hospitals_snapped.csv",
    "school": "schools_snapped.csv",
    "university": "universities_snapped.csv",
}


def main():
    print("Loading multimodal graph...")
    with open(GRAPH_DIR / "multimodal_graph.pickle", "rb") as f:
        G = pickle.load(f)
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    print("Building reversed graph...")
    G_rev = G.reverse(copy=False)

    centroids = pd.read_csv(ACC_DIR / "small_area_centroids.csv")
    results = centroids[["SA_PUB2022", "walk_node_id"]].copy()

    for category, fname in CATEGORIES.items():
        path = ACC_DIR / fname
        if not path.exists():
            print(f"WARNING: {path} not found, skipping (run script 19 first)")
            continue

        facilities = pd.read_csv(path)
        source_nodes = facilities["walk_node_id"].unique().tolist()
        print(f"\nComputing accessibility to nearest {category} ({len(source_nodes)} facilities)...")

        t0 = time.time()
        # Multi-source Dijkstra: finds shortest distance from ANY of the
        # source nodes to every other node in a single pass.
        travel_times = nx.multi_source_dijkstra_path_length(
            G_rev, sources=source_nodes, weight="travel_time"
        )
        print(f"  Reached {len(travel_times)} nodes in {time.time()-t0:.1f}s")

        col_name = f"nearest_{category}_min"
        results[col_name] = results["walk_node_id"].map(lambda n: travel_times.get(n, None))
        results[col_name] = results[col_name] / 60.0

        n_unreachable = results[col_name].isna().sum()
        print(f"  Small Areas with no path: {n_unreachable}")
        print(f"  Median travel time: {results[col_name].median():.1f} min")

    out_path = ACC_DIR / "healthcare_education_accessibility.csv"
    results.to_csv(out_path, index=False)
    print(f"\nSaved {out_path}")

    print("\nSummary:")
    for category in CATEGORIES:
        col = f"nearest_{category}_min"
        if col in results.columns:
            print(f"\n{category.upper()}:")
            print(results[col].describe())


if __name__ == "__main__":
    main()
