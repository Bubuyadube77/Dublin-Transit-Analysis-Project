"""
Script 11: Compute a population-weighted centroid for each Small Area and
snap it to the nearest walk graph node -- this is the "origin point" each
accessibility calculation starts from.

We also snap the employment destination points (script 10) to the walk
graph the same way.

INPUT:
    data/processed/boundaries/dublin_small_areas_wgs84.gpkg
    data/processed/network_graph/walk_graph.pickle
    data/processed/accessibility_scores/employment_destinations.csv

OUTPUT:
    data/processed/accessibility_scores/small_area_centroids.csv
        SA_PUB2022, lat, lon, walk_node_id, snap_distance_m
    data/processed/accessibility_scores/employment_destinations_snapped.csv
        name, lat, lon, walk_node_id, snap_distance_m

Run from the project root:
    python scripts/03_accessibility_computation/11_snap_centroids.py
"""
import pandas as pd
import geopandas as gpd
import pickle
import numpy as np
from pathlib import Path
from sklearn.neighbors import BallTree

BOUNDARY_FILE = Path("data/processed/boundaries/dublin_small_areas_wgs84.gpkg")
GRAPH_DIR = Path("data/processed/network_graph")
ACC_DIR = Path("data/processed/accessibility_scores")
ACC_DIR.mkdir(parents=True, exist_ok=True)

EARTH_RADIUS_M = 6_371_000


def build_balltree(G):
    node_ids = list(G.nodes())
    node_coords = np.array([[G.nodes[n]["y"], G.nodes[n]["x"]] for n in node_ids])
    tree = BallTree(np.radians(node_coords), metric="haversine")
    return tree, node_ids


def snap_points(tree, node_ids, lats, lons):
    coords_rad = np.radians(np.column_stack([lats, lons]))
    distances_rad, indices = tree.query(coords_rad, k=1)
    distances_m = distances_rad.flatten() * EARTH_RADIUS_M
    snapped_node_ids = [node_ids[i] for i in indices.flatten()]
    return snapped_node_ids, distances_m


def main():
    print("Loading walk graph...")
    with open(GRAPH_DIR / "walk_graph.pickle", "rb") as f:
        G = pickle.load(f)
    tree, node_ids = build_balltree(G)
    print(f"Walk graph nodes: {len(node_ids)}")

    print("\nLoading Small Area boundaries...")
    sa = gpd.read_file(BOUNDARY_FILE)
    print(f"Small Areas: {len(sa)}")

    # Geometric centroid (population-weighted would need sub-area population
    # density which we don't have -- geometric centroid is the standard
    # simplification, documented as a limitation).
    # Compute in the projected ITM CRS (accurate distances), then convert
    # back to WGS84 for snapping against the walk graph.
    sa_itm = sa.to_crs(epsg=2157)
    centroids_itm = sa_itm.geometry.centroid
    centroids_gdf = gpd.GeoDataFrame(geometry=centroids_itm, crs="EPSG:2157").to_crs(epsg=4326)
    lats = centroids_gdf.geometry.y.values
    lons = centroids_gdf.geometry.x.values

    print("Snapping Small Area centroids to walk graph...")
    snapped_nodes, distances = snap_points(tree, node_ids, lats, lons)

    centroid_df = pd.DataFrame({
        "SA_PUB2022": sa["SA_PUB2022"].values,
        "lat": lats,
        "lon": lons,
        "walk_node_id": snapped_nodes,
        "snap_distance_m": distances,
    })
    centroid_df.to_csv(ACC_DIR / "small_area_centroids.csv", index=False)
    print(f"Saved {len(centroid_df)} Small Area centroids")
    print(f"Median snap distance: {centroid_df.snap_distance_m.median():.1f}m")
    print(f"Max snap distance: {centroid_df.snap_distance_m.max():.1f}m")

    beyond = centroid_df[centroid_df.snap_distance_m > 500]
    print(f"Centroids >500m from any walk node: {len(beyond)}")

    print("\nSnapping employment destinations...")
    dest = pd.read_csv(ACC_DIR / "employment_destinations.csv")
    dest_nodes, dest_distances = snap_points(tree, node_ids, dest.lat.values, dest.lon.values)
    dest["walk_node_id"] = dest_nodes
    dest["snap_distance_m"] = dest_distances
    dest.to_csv(ACC_DIR / "employment_destinations_snapped.csv", index=False)
    print(dest[["name", "walk_node_id", "snap_distance_m"]].to_string(index=False))


if __name__ == "__main__":
    main()
