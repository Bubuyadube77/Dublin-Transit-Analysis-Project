# QGIS Mapping — Dublin Transit Deserts

## 1. Generate the layer (if you haven't already)

```bash
python scripts/04_desert_classification/14_prepare_qgis_layer.py
```

This produces `dublin_transit_deserts.gpkg` in this folder -- one layer,
5,076 Small Areas, all our accessibility/equity/classification fields
attached.

## 2. Open it in QGIS

1. Open QGIS, then **Layer > Add Layer > Add Vector Layer**
2. Browse to this folder, select `dublin_transit_deserts.gpkg`
3. It should load as a single layer called `transit_deserts`

## 3. Apply a style (two options, load whichever fits what you want to see)

QGIS doesn't auto-apply `.qml` files sitting next to a GeoPackage the way
it does for shapefiles, so load it manually:

1. Right-click the layer in the Layers panel -> **Properties**
2. Go to the **Symbology** tab
3. Click the **Style** button (bottom-left of the dialog) -> **Load Style...**
4. Browse to this folder and choose one of:
   - `dublin_transit_deserts_quadrant.qml` -- categorical map (5 colors:
     Transit Desert in red, Well-served/high-need in orange, etc.) --
     **this is the main map for the report**
   - `dublin_transit_deserts_severity.qml` -- continuous gradient by
     `desert_severity_index` (blue = well-served, red = severe desert) --
     good for a more nuanced supplementary map
5. Click **OK**, then **Apply**

## 4. What to actually look at first

Given the anomaly flagged from Stage D -- several Dun Laoghaire/Sandycove
Small Areas ranking as severe deserts despite DART line proximity -- zoom
into that area (roughly 53.28-53.30 lat, -6.11 to -6.13 lon) and cross-
reference against where you know DART stations actually sit. A few
possibilities to check:
- Are the flagged Small Areas actually FAR from the DART stations
  themselves (a genuine last-mile gap), or right next to them (suggesting
  our AM_PEAK headway calculation for DART/rail trips needs a second look)?
- Use the **Identify Features** tool (the "i" icon in the toolbar) and
  click on a flagged Small Area to see its `min_travel_time_min` and
  `nearest_destination` -- is it routing via a sensible path, or does
  something look off?

## 5. Other useful fields to symbolize/label by

- `no_car_rate` -- the raw need variable
- `min_travel_time_min` -- the raw access variable
- `ed_deprivation_category` -- for a side-by-side comparison map against
  Ahern et al.'s original deprivation-based approach
- `nearest_destination` -- which employment cluster each area is closest to
  (useful for checking if results cluster oddly around one particular
  destination point)
