"""
Script 21: Classify transit deserts for healthcare and education access,
using the same demand-supply mismatch framework as the employment analysis
(script 13), then compute overlap with the original employment-based
desert classification -- identifying areas of COMPOUNDING disadvantage
(deserts across multiple destination types simultaneously).

The NEED variable (no-car-ownership rate) is kept consistent across all
destination types, since the underlying question -- "how well does the
transit network serve people without cars" -- is the same regardless of
what they're trying to reach. This also keeps results directly comparable
across categories.

INPUT:
    data/processed/accessibility_scores/healthcare_education_accessibility.csv
    data/processed/accessibility_scores/transit_desert_classification.csv
        (for the no_car_rate / need_percentile already computed, and the
        original employment-based desert classification for comparison)

OUTPUT:
    data/processed/accessibility_scores/healthcare_education_deserts.csv
    outputs/report/compounding_disadvantage_summary.txt

Run from the project root:
    python scripts/07_multipurpose_extension/21_classify_healthcare_education_deserts.py
"""
import pandas as pd
from pathlib import Path

ACC_DIR = Path("data/processed/accessibility_scores")
OUT_DIR = Path("outputs/report")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = ["hospital", "school", "university"]


def classify(df, access_col, need_col="need_percentile"):
    access_percentile = 1 - df[access_col].rank(pct=True)
    need_percentile = df[need_col]
    severity = need_percentile - access_percentile

    def quadrant(need_pct, access_pct):
        high_need = need_pct >= 0.5
        high_access = access_pct >= 0.5
        if high_need and not high_access:
            return "Transit Desert"
        elif high_need and high_access:
            return "Well-served, high-need"
        elif not high_need and not high_access:
            return "Low-priority gap"
        else:
            return "Well-served, low-need"

    quadrants = [quadrant(n, a) for n, a in zip(need_percentile, access_percentile)]
    return access_percentile, severity, quadrants


def main():
    print("Loading data...")
    healthcare_edu = pd.read_csv(ACC_DIR / "healthcare_education_accessibility.csv")
    employment = pd.read_csv(ACC_DIR / "transit_desert_classification.csv")

    df = employment[["SA_PUB2022", "need_percentile", "no_car_rate", "quadrant",
                      "ED_ENGLISH", "COUNTY_ENGLISH"]].rename(
        columns={"quadrant": "employment_quadrant"}
    ).merge(healthcare_edu, on="SA_PUB2022", how="inner")
    print(f"Merged dataset: {len(df)} Small Areas")

    lines = []
    def log(msg):
        print(msg)
        lines.append(msg)

    log("=" * 70)
    log("COMPOUNDING DISADVANTAGE ANALYSIS")
    log("(Employment + Healthcare + Education transit desert overlap)")
    log("=" * 70)

    for category in CATEGORIES:
        access_col = f"nearest_{category}_min"
        classifiable = df.dropna(subset=[access_col, "need_percentile"]).copy()

        access_pct, severity, quadrants = classify(classifiable, access_col)
        df.loc[classifiable.index, f"{category}_access_percentile"] = access_pct.values
        df.loc[classifiable.index, f"{category}_severity"] = severity.values
        df.loc[classifiable.index, f"{category}_quadrant"] = quadrants

        n_desert = sum(q == "Transit Desert" for q in quadrants)
        log(f"\n{category.upper()} deserts: {n_desert} of {len(classifiable)} classifiable Small Areas ({100*n_desert/len(classifiable):.1f}%)")

    # --- Overlap analysis ---
    log(f"\n{'='*70}")
    log("OVERLAP: Small Areas classified as Transit Desert across MULTIPLE categories")
    log("=" * 70)

    df["is_employment_desert"] = df["employment_quadrant"] == "Transit Desert"
    for category in CATEGORIES:
        col = f"{category}_quadrant"
        if col in df.columns:
            df[f"is_{category}_desert"] = df[col] == "Transit Desert"

    desert_flags = ["is_employment_desert"] + [f"is_{c}_desert" for c in CATEGORIES if f"is_{c}_desert" in df.columns]
    df["n_desert_categories"] = df[desert_flags].sum(axis=1)

    log(f"\nDistribution of how many categories each Small Area is a desert for (0-4):")
    log(df["n_desert_categories"].value_counts().sort_index().to_string())

    compounding = df[df["n_desert_categories"] >= 3]
    log(f"\nSmall Areas that are deserts in 3+ categories (severe compounding disadvantage): {len(compounding)}")
    if len(compounding) > 0:
        log("\nTop compounding-disadvantage areas:")
        log(compounding[["SA_PUB2022", "ED_ENGLISH", "COUNTY_ENGLISH", "n_desert_categories"]]
            .sort_values("n_desert_categories", ascending=False).head(20).to_string(index=False))

    df.to_csv(ACC_DIR / "healthcare_education_deserts.csv", index=False)
    with open(OUT_DIR / "compounding_disadvantage_summary.txt", "w") as f:
        f.write("\n".join(lines))
    print(f"\nSaved healthcare_education_deserts.csv and compounding_disadvantage_summary.txt")


if __name__ == "__main__":
    main()
