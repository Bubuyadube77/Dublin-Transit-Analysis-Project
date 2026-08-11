"""
Script 17: Generate an interactive, shareable HTML web map.

Unlike the QGIS project (needs QGIS installed) or a Power BI dashboard
(needs the Power BI app), this produces a single self-contained HTML file
-- open it in any browser, or share it as a link if hosted somewhere.
Good for a portfolio page, LinkedIn post, or emailing to a recruiter.

INPUT: outputs/maps/qgis_project/dublin_transit_deserts.gpkg
OUTPUT: outputs/interactive_map/dublin_transit_deserts_interactive.html

Run from the project root:
    python scripts/06_visualization/17_generate_interactive_map.py
"""
import geopandas as gpd
import folium
from pathlib import Path

GPKG_FILE = Path("outputs/maps/qgis_project/dublin_transit_deserts.gpkg")
OUT_DIR = Path("outputs/interactive_map")
OUT_DIR.mkdir(parents=True, exist_ok=True)

QUADRANT_COLORS = {
    "Transit Desert": "#cb181d",
    "Well-served, high-need": "#fdbb84",
    "Low-priority gap": "#c7e9c0",
    "Well-served, low-need": "#31a354",
    "No data (unreachable/missing)": "#dcdcdc",
}


def style_function(feature):
    quadrant = feature["properties"].get("quadrant", "No data (unreachable/missing)")
    return {
        "fillColor": QUADRANT_COLORS.get(quadrant, "#dcdcdc"),
        "color": "#333333",
        "weight": 0.3,
        "fillOpacity": 0.75,
    }


def highlight_function(feature):
    return {"weight": 2, "color": "#000000", "fillOpacity": 0.9}


def main():
    print("Loading classified layer...")
    gdf = gpd.read_file(GPKG_FILE)
    print(f"Features: {len(gdf)}")

    # Round numeric fields for cleaner popups
    for col in ["no_car_rate", "min_travel_time_min", "desert_severity_index",
                "need_percentile", "access_percentile"]:
        if col in gdf.columns:
            gdf[col] = gdf[col].round(3)

    # Simplify geometry slightly for faster browser rendering (5m tolerance
    # in a projected CRS, then reproject back)
    gdf_simplified = gdf.copy()
    gdf_simplified["geometry"] = gdf.to_crs(epsg=2157).geometry.simplify(5).to_crs(epsg=4326)

    center_lat, center_lon = 53.35, -6.27  # Dublin city centre

    m = folium.Map(
        location=[center_lat, center_lon], zoom_start=11,
        tiles="CartoDB positron", control_scale=True,
    )

    fields = ["SA_PUB2022", "ED_ENGLISH", "COUNTY_ENGLISH", "quadrant",
              "no_car_rate", "min_travel_time_min", "nearest_destination",
              "desert_severity_index", "ed_deprivation_category"]
    aliases = ["Small Area ID", "Electoral Division", "County", "Classification",
               "No-Car Rate", "Travel Time (min)", "Nearest Employment Cluster",
               "Severity Index", "ED Deprivation Category"]

    folium.GeoJson(
        gdf_simplified,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(fields=fields, aliases=aliases, sticky=True),
        popup=folium.GeoJsonPopup(fields=fields, aliases=aliases),
        name="Transit Desert Classification",
    ).add_to(m)

    # Legend (folium doesn't auto-generate one for GeoJson, so add manually)
    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background-color: white; padding: 12px 16px; border-radius: 6px;
                box-shadow: 0 1px 6px rgba(0,0,0,0.3); font-family: sans-serif; font-size: 13px;">
      <b>Transit Desert Classification</b><br>
    """
    for label, color in QUADRANT_COLORS.items():
        legend_html += (
            f'<span style="display:inline-block;width:12px;height:12px;'
            f'background:{color};margin-right:6px;border:1px solid #333;"></span>{label}<br>'
        )
    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    title_html = """
    <div style="position: fixed; top: 15px; left: 60px; z-index: 1000;
                background-color: white; padding: 8px 16px; border-radius: 6px;
                box-shadow: 0 1px 6px rgba(0,0,0,0.3); font-family: sans-serif;">
      <b style="font-size:16px;">Transit Deserts in the Greater Dublin Area</b><br>
      <span style="font-size:12px;color:#555;">Click any area for details \u00B7 Data: TFI GTFS, CSO Census 2022, Pobal HP Deprivation Index</span>
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    folium.LayerControl().add_to(m)

    out_path = OUT_DIR / "dublin_transit_deserts_interactive.html"
    m.save(str(out_path))
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()
