"""
Script 15: Equity overlay statistics (Stage E)

Produces the quantitative backbone for the report's Results/Discussion
sections:
    1. Correlation between desert severity and income deprivation
       (a distinct question from the classification itself -- tests
       whether deserts and deprivation are statistically related, and
       how strongly, independent of the quadrant classification)
    2. Chi-square test: is desert status independent of deprivation
       category, or is there a real statistical relationship?
    3. ED-level rollup of our Small-Area results -- lets us directly
       compare against Ahern et al. (2016), who worked at ED level
    4. A clean, ranked priority zone table for the report's
       site-specific-narratives section

INPUT:
    data/processed/accessibility_scores/transit_desert_classification.csv

OUTPUT:
    outputs/report/equity_stats_summary.txt   (human-readable stats writeup)
    outputs/report/ed_level_rollup.csv
    outputs/report/priority_zones_top30.csv

Run from the project root:
    python scripts/05_equity_overlay/15_equity_stats.py
"""
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

CLASSIFICATION_FILE = Path("data/processed/accessibility_scores/transit_desert_classification.csv")
OUT_DIR = Path("outputs/report")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    df = pd.read_csv(CLASSIFICATION_FILE)
    print(f"Loaded {len(df)} classified Small Areas")

    lines = []  # collect human-readable summary for the text file
    def log(msg):
        print(msg)
        lines.append(msg)

    log("=" * 70)
    log("DUBLIN TRANSIT DESERT ANALYSIS -- EQUITY STATISTICS SUMMARY")
    log("=" * 70)

    # --- 1. Correlation: desert severity vs deprivation score ---
    # Drop rows missing either variable (deprivation is ED-level so every
    # SA within a matched ED has a value, but guard anyway)
    corr_df = df.dropna(subset=["desert_severity_index", "ed_deprivation_score"])
    log(f"\n[1] CORRELATION: Desert Severity Index vs Pobal Deprivation Score")
    log(f"    (n = {len(corr_df)} Small Areas)")

    pearson_r, pearson_p = stats.pearsonr(corr_df["desert_severity_index"], corr_df["ed_deprivation_score"])
    spearman_r, spearman_p = stats.spearmanr(corr_df["desert_severity_index"], corr_df["ed_deprivation_score"])

    log(f"    Pearson r  = {pearson_r:.4f}  (p = {pearson_p:.4g})")
    log(f"    Spearman rho = {spearman_r:.4f}  (p = {spearman_p:.4g})")
    log(f"    NOTE: deprivation score is coded so HIGHER = more affluent,")
    log(f"    so a NEGATIVE correlation means deserts skew toward more")
    log(f"    deprived areas -- interpret sign carefully in the writeup.")

    # --- 2. Chi-square: is desert status independent of deprivation category? ---
    log(f"\n[2] CHI-SQUARE TEST: Desert status vs Deprivation category")
    df["is_desert"] = df["quadrant"] == "Transit Desert"
    contingency = pd.crosstab(df["is_desert"], df["ed_deprivation_category"])
    log(f"\n{contingency.to_string()}")

    chi2, chi_p, dof, expected = stats.chi2_contingency(contingency)
    log(f"\n    Chi-square = {chi2:.4f}, p = {chi_p:.4g}, dof = {dof}")
    if chi_p < 0.05:
        log(f"    -> Statistically significant relationship (p < 0.05):")
        log(f"       desert status is NOT independent of deprivation category.")
    else:
        log(f"    -> No statistically significant relationship found (p >= 0.05).")

    # --- 3. ED-level rollup for comparison against Ahern et al. ---
    log(f"\n[3] ELECTORAL DIVISION (ED) LEVEL ROLLUP")
    log(f"    (for direct comparison against Ahern et al. 2016, which worked at ED level)")

    ed_rollup = df.groupby(["ED_ID_STR", "ED_ENGLISH", "COUNTY_ENGLISH"]).agg(
        n_small_areas=("SA_PUB2022", "count"),
        n_deserts=("is_desert", "sum"),
        mean_severity_index=("desert_severity_index", "mean"),
        mean_no_car_rate=("no_car_rate", "mean"),
        mean_travel_time_min=("min_travel_time_min", "mean"),
        deprivation_score=("ed_deprivation_score", "first"),
        deprivation_category=("ed_deprivation_category", "first"),
    ).reset_index()
    ed_rollup["pct_desert"] = 100 * ed_rollup["n_deserts"] / ed_rollup["n_small_areas"]
    ed_rollup = ed_rollup.sort_values("pct_desert", ascending=False)

    ed_rollup.to_csv(OUT_DIR / "ed_level_rollup.csv", index=False)
    log(f"    Saved ed_level_rollup.csv ({len(ed_rollup)} EDs)")

    log(f"\n    Top 10 EDs by % of Small Areas classified as Transit Desert:")
    log(ed_rollup[[
        "ED_ENGLISH", "COUNTY_ENGLISH", "n_small_areas", "n_deserts",
        "pct_desert", "deprivation_category"
    ]].head(10).to_string(index=False))

    # --- 4. Priority zone list ---
    log(f"\n[4] PRIORITY ZONES (top 30 by desert severity index)")
    priority = df[df["is_desert"]].sort_values("desert_severity_index", ascending=False).head(30)
    priority_out = priority[[
        "SA_PUB2022", "ED_ENGLISH", "COUNTY_ENGLISH", "no_car_rate",
        "min_travel_time_min", "nearest_destination", "desert_severity_index",
        "ed_deprivation_category", "ed_deprivation_score",
    ]]
    priority_out.to_csv(OUT_DIR / "priority_zones_top30.csv", index=False)
    log(f"    Saved priority_zones_top30.csv")

    # --- 5. Overall summary numbers for the report abstract/executive summary ---
    log(f"\n[5] HEADLINE NUMBERS")
    total = len(df)
    n_desert = df["is_desert"].sum()
    log(f"    Total classifiable Small Areas: {total}")
    log(f"    Transit Deserts identified: {n_desert} ({100*n_desert/total:.1f}%)")

    # Bring in population to give a headline "X people live in transit deserts"
    try:
        census = pd.read_csv("data/raw/census/dublin_small_area_saps.csv")
        pop_lookup = census.set_index("GEOGID")["T1_1AGETT"]
        df["population"] = df["SA_PUB2022"].map(pop_lookup)
        total_pop = df["population"].sum()
        desert_pop = df.loc[df["is_desert"], "population"].sum()
        log(f"    Total population (classifiable Small Areas): {total_pop:,.0f}")
        log(f"    Population living in Transit Deserts: {desert_pop:,.0f} ({100*desert_pop/total_pop:.1f}%)")
    except Exception as e:
        log(f"    Could not compute population figures: {e}")

    with open(OUT_DIR / "equity_stats_summary.txt", "w") as f:
        f.write("\n".join(lines))
    print(f"\nFull summary written to {OUT_DIR / 'equity_stats_summary.txt'}")


if __name__ == "__main__":
    main()
