# Multi-Purpose Accessibility Extension (Stage F)

Fulfills research gap #5 (employment-only focus), previously deferred.
Extends the analysis to healthcare and education destinations using OSM
data, and identifies areas of COMPOUNDING disadvantage -- deserts across
multiple destination types simultaneously.

Run after Stage E (05_equity_overlay) is complete.

```bash
python scripts/07_multipurpose_extension/18_extract_healthcare_education_pois.py
python scripts/07_multipurpose_extension/19_snap_healthcare_education.py
python scripts/07_multipurpose_extension/20_compute_healthcare_education_access.py
python scripts/07_multipurpose_extension/21_classify_healthcare_education_deserts.py
```

Note: script 18 needs `data/raw/osm/dublin_extract.osm.pbf`. If you deleted
it after Stage A, re-run script 05_clip_osm.py from Stage A first.

## What each script produces

| Script | Output |
|---|---|
| 18 | `hospitals.csv`, `schools.csv`, `universities.csv` (OSM-extracted points) |
| 19 | Same files with `_snapped` suffix -- walk graph node assignments |
| 20 | `healthcare_education_accessibility.csv` -- travel time to nearest facility of each type, per Small Area |
| 21 | `healthcare_education_deserts.csv`, `compounding_disadvantage_summary.txt` |

## Method notes

- **62 hospitals, 693 schools (682 after dedup), 136 universities/colleges**
  extracted from OSM for the Dublin Region.
- **Multi-source Dijkstra**, not per-facility search: finds "nearest
  facility of this type" for every Small Area in a single graph pass per
  category, rather than searching each individual facility separately
  and taking the minimum (which would mean ~891 separate searches instead
  of 3).
- The NEED variable (no-car-ownership rate) is kept consistent across all
  categories -- the underlying equity question is the same regardless of
  destination type, and this keeps results comparable.

## Key results from testing

- Median travel time: 8.4 min (school), 17.7 min (university), 19.9 min
  (hospital) -- reflects facility density (schools are neighbourhood-level,
  hospitals/universities more centralised).
- Desert counts: Hospital 743 (15.1%), School 923 (18.7%), University 620
  (12.6%), vs. Employment 854 (17.3%) from the original analysis.
- **491 Small Areas are deserts in 3+ categories** -- genuine compounding
  disadvantage, not just single-purpose access gaps.
- **133 Small Areas are deserts in ALL FOUR categories** -- the most
  severely underserved areas in the Dublin Region across every destination
  type tested.
- Geographic spread is broader than the employment-only findings: Ballygall,
  Rathmines, Finglas South, Tallaght-Jobstown, Clondalkin (multiple EDs),
  Lucan, Baldoyle, and Balbriggan Rural all appear -- covering all four
  Dublin local authorities, not just Dublin City.
