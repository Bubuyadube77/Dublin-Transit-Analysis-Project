"""
Script 09: Build the final unified multimodal graph.

Combines:
    - The walk network graph (script 06)
    - Transit ride edges, stop-to-stop (script 07)
    - Headway/wait-time data (script 07)
    - Stop-to-walk-node snapping (script 08)

Graph structure:
    - Walk nodes: OSM node IDs, connected by walk edges (weight = seconds)
    - Transit stop nodes: prefixed "stop_<stop_id>" to avoid ID collisions
    - "board" edges: walk_node -> stop_node, weight = wait_time_seconds
    - "alight" edges: stop_node -> walk_node, weight = fixed alighting time
    - "ride" edges: stop_node -> stop_node, weight = median in-vehicle time

NOTE ON SCOPE: this first version builds the graph using AM_PEAK wait times
as the representative scenario (the standard "can you get to work on time"
accessibility question). Stops with no AM_PEAK service fall back to the
average wait time across whatever periods they do have data for. Building
separate graphs per time period is a natural extension once this baseline
is working -- flag this as a limitation / future work in the report.

INPUT:
    data/processed/network_graph/walk_graph.pickle
    data/processed/network_graph/transit_edges.csv
    data/processed/network_graph/stop_headways.csv
    data/processed/network_graph/stop_to_walk_node.csv

OUTPUT:
    data/processed/network_graph/multimodal_graph.pickle

Run from the project root:
    python scripts/02_network_construction/09_build_multimodal_graph.py
"""
import pandas as pd
import pickle
import networkx as nx
from pathlib import Path

GRAPH_DIR = Path("data/processed/network_graph")

ALIGHT_TIME_SECONDS = 15  # small fixed penalty for disembarking
ANALYSIS_PERIOD = "AM_PEAK"


def main():
    print("Loading walk graph...")
    with open(GRAPH_DIR / "walk_graph.pickle", "rb") as f:
        G = pickle.load(f)
    print(f"Walk graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Convert to a directed graph -- transit edges are inherently directional
    # (a bus route doesn't necessarily run the same speed/path both ways),
    # while walk edges are treated as bidirectional (same cost either way).
    G = G.to_directed()

    print("Loading transit data...")
    transit_edges = pd.read_csv(GRAPH_DIR / "transit_edges.csv")
    headways = pd.read_csv(GRAPH_DIR / "stop_headways.csv")
    snap = pd.read_csv(GRAPH_DIR / "stop_to_walk_node.csv")

    # --- Determine wait time per stop for the analysis period ---
    am_peak = headways[headways.period == ANALYSIS_PERIOD].set_index("stop_id")["wait_time_seconds"]
    fallback = headways.groupby("stop_id")["wait_time_seconds"].mean()
    wait_time_by_stop = am_peak.combine_first(fallback).to_dict()

    stops_with_no_wait_data = set(snap.stop_id) - set(wait_time_by_stop.keys())
    print(f"Stops with no headway data at all (will get a large default wait): {len(stops_with_no_wait_data)}")
    DEFAULT_WAIT_SECONDS = 15 * 60  # 15 min, conservative fallback

    # --- Add transit stop nodes ---
    print("Adding transit stop nodes...")
    snap_lookup = snap.set_index("stop_id")["walk_node_id"].to_dict()
    for stop_id in snap.stop_id:
        stop_node_id = f"stop_{stop_id}"
        G.add_node(stop_node_id, node_type="transit_stop", stop_id=stop_id)

    # --- Add board/alight edges connecting walk nodes to stop nodes ---
    print("Adding board/alight edges...")
    board_count = 0
    for _, row in snap.iterrows():
        stop_id = row["stop_id"]
        walk_node_id = row["walk_node_id"]
        stop_node_id = f"stop_{stop_id}"
        wait_time = wait_time_by_stop.get(stop_id, DEFAULT_WAIT_SECONDS)

        G.add_edge(walk_node_id, stop_node_id, travel_time=wait_time, edge_type="board")
        G.add_edge(stop_node_id, walk_node_id, travel_time=ALIGHT_TIME_SECONDS, edge_type="alight")
        board_count += 1
    print(f"Added {board_count} board/alight edge pairs")

    # --- Add ride edges between stops (median travel time across trips) ---
    print("Aggregating and adding ride edges...")
    ride_agg = transit_edges.groupby(["from_stop", "to_stop"])["travel_time_seconds"].median().reset_index()
    for _, row in ride_agg.iterrows():
        from_node = f"stop_{row['from_stop']}"
        to_node = f"stop_{row['to_stop']}"
        G.add_edge(from_node, to_node, travel_time=row["travel_time_seconds"], edge_type="ride")
    print(f"Added {len(ride_agg)} ride edges")

    print(f"\nFinal multimodal graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Sanity check: connectivity
    largest_cc = max(nx.weakly_connected_components(G), key=len)
    pct = 100 * len(largest_cc) / G.number_of_nodes()
    print(f"Largest weakly connected component: {len(largest_cc)} nodes ({pct:.1f}%)")

    with open(GRAPH_DIR / "multimodal_graph.pickle", "wb") as f:
        pickle.dump(G, f)
    print("\nSaved multimodal_graph.pickle")


if __name__ == "__main__":
    main()
