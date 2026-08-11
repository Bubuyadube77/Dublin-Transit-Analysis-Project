"""
Script 16: Generate static, report-ready map exports.

Produces publication-quality PNG maps directly from the classified
GeoPackage using matplotlib/geopandas -- reproducible from code (better
for a methodology section than a manually-styled QGIS screenshot), though
you can still use the QGIS project for interactive exploration.

INPUT: outputs/maps/qgis_project/dublin_transit_deserts.gpkg
OUTPUT: outputs/maps/static_exports/*.png

Run from the project root:
    python scripts/06_visualization/16_generate_static_maps.py
"""
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

GPKG_FILE = Path("outputs/maps/qgis_project/dublin_transit_deserts.gpkg")
OUT_DIR = Path("outputs/maps/static_exports")
OUT_DIR.mkdir(parents=True, exist_ok=True)

QUADRANT_COLORS = {
    "Transit Desert": "#cb181d",
    "Well-served, high-need": "#fdbb84",
    "Low-priority gap": "#c7e9c0",
    "Well-served, low-need": "#31a354",
    "No data (unreachable/missing)": "#dcdcdc",
}

FIG_DPI = 300


def main():
    print("Loading classified layer...")
    gdf = gpd.read_file(GPKG_FILE)
    print(f"Features: {len(gdf)}")

    # --- Map 1: Quadrant classification (the main report figure) ---
    print("Generating quadrant classification map...")
    fig, ax = plt.subplots(figsize=(10, 12))
    for category, color in QUADRANT_COLORS.items():
        subset = gdf[gdf["quadrant"] == category]
        subset.plot(ax=ax, color=color, edgecolor="#333333", linewidth=0.05)

    # County boundaries overlay for geographic context
    county_boundary = gdf.dissolve(by="COUNTY_ENGLISH")
    county_boundary.boundary.plot(ax=ax, color="black", linewidth=0.6)

    ax.set_title("Transit Deserts in the Greater Dublin Area\n(Demand-Supply Mismatch Classification, 2026)",
                  fontsize=14, fontweight="bold")
    ax.set_axis_off()

    legend_patches = [mpatches.Patch(color=c, label=l) for l, c in QUADRANT_COLORS.items()]
    ax.legend(handles=legend_patches, loc="lower left", fontsize=9, frameon=True, title="Classification")

    ax.annotate(
        "Data: TFI GTFS (Aug 2026), CSO Census 2022, Pobal HP Deprivation Index\n"
        "Method: GTFS-based multimodal accessibility + demand-supply mismatch framework",
        xy=(0.01, 0.01), xycoords="figure fraction", fontsize=7, color="#555555"
    )

    plt.tight_layout()
    plt.savefig(OUT_DIR / "01_quadrant_classification.png", dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print("Saved 01_quadrant_classification.png")

    # --- Map 2: Continuous severity gradient ---
    print("Generating severity gradient map...")
    fig, ax = plt.subplots(figsize=(10, 12))
    gdf.plot(
        column="desert_severity_index", ax=ax, cmap="RdYlBu_r",
        edgecolor="#333333", linewidth=0.05, legend=True,
        legend_kwds={"label": "Desert Severity Index (higher = more severe)", "shrink": 0.5},
        missing_kwds={"color": "#dcdcdc"},
    )
    county_boundary.boundary.plot(ax=ax, color="black", linewidth=0.6)
    ax.set_title("Transit Desert Severity Index\nGreater Dublin Area, 2026",
                  fontsize=14, fontweight="bold")
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "02_severity_gradient.png", dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print("Saved 02_severity_gradient.png")

    # --- Map 3: No-car ownership rate (the NEED variable alone) ---
    print("Generating no-car ownership map...")
    fig, ax = plt.subplots(figsize=(10, 12))
    gdf.plot(
        column="no_car_rate", ax=ax, cmap="Purples",
        edgecolor="#333333", linewidth=0.05, legend=True,
        legend_kwds={"label": "Share of households with no car", "shrink": 0.5},
        missing_kwds={"color": "#dcdcdc"},
    )
    county_boundary.boundary.plot(ax=ax, color="black", linewidth=0.6)
    ax.set_title("No-Car Household Rate\nGreater Dublin Area, Census 2022",
                  fontsize=14, fontweight="bold")
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "03_no_car_rate.png", dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print("Saved 03_no_car_rate.png")

    # --- Map 4: Travel time to nearest employment cluster (the ACCESS variable alone) ---
    print("Generating travel time map...")
    fig, ax = plt.subplots(figsize=(10, 12))
    gdf.plot(
        column="min_travel_time_min", ax=ax, cmap="YlOrRd",
        edgecolor="#333333", linewidth=0.05, legend=True,
        legend_kwds={"label": "Travel time to nearest employment cluster (min)", "shrink": 0.5},
        missing_kwds={"color": "#dcdcdc"}, vmax=90,
    )
    county_boundary.boundary.plot(ax=ax, color="black", linewidth=0.6)
    ax.set_title("Transit Travel Time to Nearest Major Employment Cluster\nGreater Dublin Area, AM Peak",
                  fontsize=14, fontweight="bold")
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "04_travel_time.png", dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print("Saved 04_travel_time.png")

    print(f"\nAll maps saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
