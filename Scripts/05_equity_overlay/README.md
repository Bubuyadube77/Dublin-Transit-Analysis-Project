# Equity Overlay Statistics (Stage E)

Run after Stage D (04_desert_classification) is complete.

```bash
python scripts/05_equity_overlay/15_equity_stats.py
```

No new dependencies beyond scipy:
```bash
conda install -c conda-forge scipy -y
```

## Output

- `outputs/report/equity_stats_summary.txt` -- full human-readable stats writeup, ready to paste into the report
- `outputs/report/ed_level_rollup.csv` -- ED-level aggregation for direct comparison against Ahern et al. (2016)
- `outputs/report/priority_zones_top30.csv` -- ranked list for the site-specific-narratives report section

## Key results from testing

- **Correlation:** Pearson r = -0.190 (p < 0.001) between desert severity
  and Pobal deprivation score. Statistically significant, though a modest
  effect size -- confirms deserts and deprivation are related but distinct
  phenomena (deprivation score is coded so higher = more affluent, hence
  the negative sign).
- **Chi-square:** χ² = 214.5, p < 0.001 -- desert status is NOT independent
  of deprivation category.
- **Headline numbers:** 854 Small Areas (17.3%) classified as Transit
  Desert, home to 233,825 people (16.6% of the classifiable Dublin Region
  population).
- **Striking finding:** several EDs show 100% of their Small Areas
  classified as deserts -- Priorswood B/C/D, Kimmage A/B/D, Kilmore B/C,
  Cherry Orchard A, Crumlin E, all in Dublin City. These are real, named
  neighborhoods with documented socioeconomic histories, which strengthens
  the report's site-specific narrative section considerably.
