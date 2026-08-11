# Accessibility Computation Scripts (Stage C, Option A: Employment-focused)

Run these in order, after Stage B (02_network_construction) is complete.

```bash
python scripts/03_accessibility_computation/10_define_destinations.py
python scripts/03_accessibility_computation/11_snap_centroids.py
python scripts/03_accessibility_computation/12_compute_accessibility.py
```

## IMPORTANT: verify destination coordinates first

Script 10 uses hand-specified coordinates for six major Dublin employment
clusters (CBD, IFSC, Sandyford, Airport, Blanchardstown, Tallaght). These
are reasonable approximations but should be spot-checked against Google
Maps/OSM before trusting the final results -- edit the CSV it produces
directly if any need correcting, then re-run scripts 11 and 12.

## What each script produces

| Script | Output |
|---|---|
| 10 | `employment_destinations.csv` -- the 6 destination points |
| 11 | `small_area_centroids.csv`, `employment_destinations_snapped.csv` |
| 12 | `accessibility_scores.csv` -- the core result: travel time from every Small Area to every destination, plus minimum/nearest |

## Method notes

- **Centroids:** geometric centroid of each Small Area polygon (not
  population-weighted, since we don't have sub-area population density --
  documented as a limitation).
- **Efficiency trick:** rather than running 5,076 separate shortest-path
  searches (one per Small Area -- far too slow), we reverse the graph and
  run a single search FROM each of the 6 destinations, which computes
  travel time to every other node in one pass. Mathematically equivalent,
  vastly faster (~4 seconds per destination vs. what would likely be hours
  the naive way).
- **Known limitation:** ~147 Small Areas (2.9%) sit on small islands of the
  OSM walk network that aren't connected to the main street graph -- likely
  missing footway links in OSM's crowdsourced data (seen in areas like
  Pembroke West, Rathmines West, Cabra East). These show up as unreachable
  (NaN) in the results. Worth a line in the report's data limitations
  section. Could be fixed later by loosening graph connectivity rules if
  time allows, but isn't blocking progress.

## Results snapshot from testing

- 4,929 of 5,076 Small Areas successfully scored
- Mean travel time to nearest employment cluster: 30.1 minutes
- Median: 29.3 minutes
- Range: 1.0 to 124.6 minutes (the high end flags real edge-of-region areas
  worth checking individually later)
