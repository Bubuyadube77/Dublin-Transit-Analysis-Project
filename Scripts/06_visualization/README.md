# Static Map Exports (Visualization)

Run after Stage D (04_desert_classification), specifically after script 14
has produced the GeoPackage.

```bash
conda install -c conda-forge matplotlib -y
python scripts/06_visualization/16_generate_static_maps.py
```

## Output (all in outputs/maps/static_exports/, 300 DPI, report-ready)

1. `01_quadrant_classification.png` -- the main figure: 5-category desert
   classification map. This is the one to lead the Results section with.
2. `02_severity_gradient.png` -- continuous severity index, arguably more
   analytically interesting than the categorical version. Highlights a
   striking severe cluster in north Fingal alongside the expected
   Priorswood/inner-city cluster.
3. `03_no_car_rate.png` -- the raw NEED variable alone. Good "sanity check"
   figure showing the underlying data behaves as expected (classic urban
   density gradient, concentrated in the inner city) before classification
   is applied.
4. `04_travel_time.png` -- the raw ACCESS variable alone. Clearest of the
   four -- a clean radial gradient from the CBD outward, validating the
   whole accessibility computation visually in one image.

## Notes

- These are generated directly from code (matplotlib/geopandas), not
  QGIS screenshots -- more reproducible for a methodology section, and
  easier to regenerate if the underlying classification changes.
- The interactive QGIS project (outputs/maps/qgis_project/) is still
  useful for exploration and spot-checking specific areas (like we did
  for the Dun Laoghaire/DART investigation) -- keep using both.
- Travel time map is capped at vmax=90 min for readable color contrast;
  a handful of far-edge areas exceed this and will show as solid dark red
  rather than a distinct shade.
