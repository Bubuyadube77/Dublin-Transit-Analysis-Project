"""
Script 06: Extract the walking network and build a networkx graph

Run script 05 first (or point INPUT_PBF below at the full national file if
your machine has enough RAM to skip clipping).

INPUT: data/raw/osm/dublin_extract.osm.pbf
OUTPUT: data/processed/network_graph/walk_graph.pickle
        data/raw/osm/dublin_walk_network.gpkg (edges as a GeoPackage, for QGIS)

Run from the project root:
    python scripts/01_data_ingestion/06_build_walk_graph.py
"""
from pyrosm import OSM
import pandas as pd
import geopandas as gpd
import networkx as nx
import pickle
import time
from pathlib import Path

INPUT_PBF = Path("data/raw/osm/dublin_extract.osm.pbf")
GRAPH_OUT = Path("data/processed/network_graph")
OSM_OUT = Path("data/raw/osm")
GRAPH_OUT.mkdir(parents=True, exist_ok=True)

WALK_SPEED_MPS = 1.25  # ~4.5 km/h, standard pedestrian walking speed assumption


def main():
    t0 = time.time()
    print("Loading OSM extract...")
    osm = OSM(str(INPUT_PBF))

    print("Extracting walking network (nodes + edges)...")
    nodes, edges = osm.get_network(network_type="walking", nodes=True)
    print(f"Nodes: {len(nodes)}, Edges: {len(edges)}  ({time.time()-t0:.1f}s)")

    # Save the full edges as a GeoPackage for QGIS visualization
    edges.to_file(OSM_OUT / "dublin_walk_network.gpkg", driver="GPKG")
    print("Saved dublin_walk_network.gpkg for QGIS")

    # Slim down to just what's needed for the graph (keeps memory low)
    edges_slim = edges[["u", "v", "length", "geometry", "highway"]].copy()
    nodes_slim = nodes[["id", "lon", "lat"]].copy()

    node_coords = dict(zip(nodes_slim["id"], zip(nodes_slim["lon"], nodes_slim["lat"])))

    G = nx.Graph()
    used_node_ids = set(edges_slim["u"]).union(set(edges_slim["v"]))
    print(f"Unique nodes used as edge endpoints: {len(used_node_ids)}")

    for nid in used_node_ids:
        if nid in node_coords:
            lon, lat = node_coords[nid]
            G.add_node(nid, x=lon, y=lat)

    edge_tuples = list(zip(edges_slim["u"], edges_slim["v"], edges_slim["length"], edges_slim["highway"]))
    for u, v, length, highway in edge_tuples:
        if pd.isna(length) or length <= 0:
            continue
        travel_time_s = length / WALK_SPEED_MPS
        G.add_edge(u, v, length=length, travel_time=travel_time_s, highway=highway)

    print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges  ({time.time()-t0:.1f}s)")

    largest_cc = max(nx.connected_components(G), key=len)
    pct = 100 * len(largest_cc) / G.number_of_nodes()
    print(f"Largest connected component: {len(largest_cc)} of {G.number_of_nodes()} nodes ({pct:.1f}%)")

    with open(GRAPH_OUT / "walk_graph.pickle", "wb") as f:
        pickle.dump(G, f)
    print(f"\nSaved walk_graph.pickle. Total time {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
