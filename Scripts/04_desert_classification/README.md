# Transit Desert Classification Scripts (Stage D)

Run after Stage C (03_accessibility_computation) is complete.

```bash
python scripts/04_desert_classification/13_classify_deserts.py
```

## Method

Formal demand-supply mismatch framework (Jiao & Dillivan), not just raw
low accessibility:

1. NEED score = no-car-ownership rate per Small Area (Census 2022)
2. ACCESS score = travel time to nearest employment cluster (Stage C)
3. Percentile-rank both, classify into a 2x2 quadrant via median split:
   - High need + Low access -> **Transit Desert**
   - High need + High access -> Well-served, high-need
   - Low need + Low access -> Low-priority gap
   - Low need + High access -> Well-served, low-need
4. Continuous **desert_severity_index** = need_percentile - access_percentile
   for gradient mapping (roughly -1 to +1)

Pobal ED-level deprivation is attached for comparison only (not used in
the primary classification, since it's only available at the coarser ED
level, not Small Area).

## Output

`data/processed/accessibility_scores/transit_desert_classification.csv`

## Results snapshot from testing

- 4,926 of 5,076 Small Areas classifiable (have both need + access data)
- 854 Transit Deserts identified (17.3%)
- Notably: deserts and deprivation only partially overlap -- only 20 of
  854 deserts are in "Very Disadvantaged" EDs, while 296 are in
  "Marginally Above Average" EDs. This supports using the demand-supply
  framework rather than deprivation alone as the desert indicator.

## Worth investigating once you can map this

Several Dun Laoghaire/Sandycove/Glenageary Small Areas rank among the most
severe deserts despite DART line proximity, which should offer strong CBD
access. Could be a genuine last-mile gap, or could reflect how DART
frequency is being captured in the AM_PEAK headway calculation from Stage
B. Worth a spot-check once you can see this on a map.
