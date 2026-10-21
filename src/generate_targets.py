"""
Synthetic Target Quota Generator Module
Business Performance Diagnosis & Decision Intelligence Platform

GOVERNANCE DECLARATION:
This module generates 100% SYNTHETIC managerial budget quotas for target-vs-actual
variance modeling. It does NOT represent actual internal corporate data.
Fixed random seed (seed=42) ensures exact deterministic reproducibility (576 rows).
"""

from pathlib import Path
import numpy as np
import pandas as pd


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def generate_synthetic_targets() -> pd.DataFrame:
    root = get_project_root()
    clean_path = root / "data" / "processed" / "clean_transactions.csv"
    if not clean_path.exists():
        raise FileNotFoundError(f"Clean transactions missing at: {clean_path}")

    df_clean = pd.read_csv(clean_path)
    df_clean["Order Date"] = pd.to_datetime(df_clean["Order Date"])
    df_clean["YearMonth"] = df_clean["Order Date"].dt.to_period("M")

    # Calculate actual baseline historical monthly total sales by Region & Category
    monthly_totals = df_clean.groupby(["YearMonth", "Region", "Category"])["Sales"].sum()
    actual_monthly = monthly_totals.groupby(["Region", "Category"]).mean().to_dict()

    years = [2015, 2016, 2017, 2018]
    months = list(range(1, 13))
    regions = sorted(df_clean["Region"].unique().tolist())      # ['Central', 'East', 'South', 'West']
    categories = sorted(df_clean["Category"].unique().tolist()) # ['Furniture', 'Office Supplies', 'Technology']

    # Deterministic Random Generator with fixed seed 42
    rng = np.random.default_rng(42)

    records = []
    target_id = 1

    # Annual target growth rates expected by executive management
    year_growth = {2015: 1.00, 2016: 1.08, 2017: 1.18, 2018: 1.30}

    # Seasonal multipliers reflecting real-world retail cadence (Q4 peak)
    seasonal_weights = {
        1: 0.75, 2: 0.70, 3: 0.85, 4: 0.80, 5: 0.90, 6: 0.95,
        7: 0.90, 8: 0.95, 9: 1.15, 10: 1.10, 11: 1.45, 12: 1.50
    }

    # Benchmark target profit margin set by CFO (15.0% target margin)
    benchmark_margin = 0.150

    for year in years:
        growth = year_growth[year]
        for month in months:
            season = seasonal_weights[month]
            date_key = int(f"{year}{month:02d}01")
            year_month = f"{year}-{month:02d}"

            for region in regions:
                for category in categories:
                    base_sales = actual_monthly.get((region, category), 2500.0) * 12 / 12

                    # Managerial stretch factor with controlled realistic perturbation (-12% to +10%)
                    noise = rng.uniform(-0.12, 0.10)
                    target_revenue = round(float(base_sales * growth * season * (1.0 + noise)), 2)

                    # Ensure target revenue is strictly positive
                    target_revenue = max(target_revenue, 500.0)

                    # Target profit derived with benchmark margin +/- 1.5% margin tolerance
                    margin_noise = rng.uniform(-0.015, 0.015)
                    target_margin = round(benchmark_margin + margin_noise, 4)
                    target_profit = round(float(target_revenue * target_margin), 2)

                    records.append({
                        "TargetID": target_id,
                        "TargetDateKey": date_key,
                        "Year": year,
                        "Month": month,
                        "YearMonth": year_month,
                        "Region": region,
                        "Category": category,
                        "TargetRevenue": target_revenue,
                        "TargetProfit": target_profit,
                        "TargetMarginPct": target_margin,
                        "TargetType": "Synthetic Managerial Budget Target"
                    })
                    target_id += 1

    df_targets = pd.DataFrame(records)

    out_path = root / "data" / "processed" / "fact_targets.csv"
    df_targets.to_csv(out_path, index=False)

    print("=" * 70)
    print("STAGE 4: SYNTHETIC TARGET QUOTA GENERATION COMPLETED")
    print("=" * 70)
    print(f"Generated Target Rows : {len(df_targets)} (Expected: 576)")
    print(f"Time Horizon          : 2015-01 to 2018-12 (48 Months)")
    print(f"Total Target Revenue  : ${df_targets['TargetRevenue'].sum():,.2f}")
    print(f"Total Target Profit   : ${df_targets['TargetProfit'].sum():,.2f}")
    print(f"Blended Target Margin : {(df_targets['TargetProfit'].sum() / df_targets['TargetRevenue'].sum() * 100):.2f}%")
    print(f"Output Destination    : {out_path.name}")
    print(f"Governance Check      : Labeled as 'Synthetic Managerial Budget Target' (Seed=42)")
    return df_targets


if __name__ == "__main__":
    generate_synthetic_targets()
