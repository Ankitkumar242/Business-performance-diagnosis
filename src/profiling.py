"""
Data Profiling Module
Business Performance Diagnosis & Decision Intelligence Platform

Performs deep profiling of dataset before and after cleaning.
Detects nulls, duplicates, date anomalies, negative values, and statistical outliers.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def detect_outliers_iqr(series: pd.Series) -> dict:
    """Calculates outlier count and bounds using Tukey's IQR method."""
    clean_series = series.dropna()
    if len(clean_series) == 0:
        return {"q1": 0, "q3": 0, "iqr": 0, "lower_bound": 0, "upper_bound": 0, "outlier_count": 0, "outlier_pct": 0.0}
    q1 = float(np.percentile(clean_series, 25))
    q3 = float(np.percentile(clean_series, 75))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = clean_series[(clean_series < lower_bound) | (clean_series > upper_bound)]
    return {
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "iqr": round(iqr, 4),
        "lower_bound": round(lower_bound, 4),
        "upper_bound": round(upper_bound, 4),
        "outlier_count": int(len(outliers)),
        "outlier_pct": round(float(len(outliers) / len(clean_series) * 100), 2),
    }


def generate_profile(df: pd.DataFrame, profile_name: str = "Pre-Cleaning Profile") -> dict:
    """Generates an extensive data quality profile dictionary for a DataFrame."""
    total_rows = len(df)
    total_cols = len(df.columns)

    # 1. Column-level Null and Type Audit
    column_stats = {}
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        null_pct = round((null_count / total_rows) * 100, 2)
        distinct_count = int(df[col].nunique(dropna=True))
        column_stats[col] = {
            "dtype": str(df[col].dtype),
            "null_count": null_count,
            "null_pct": null_pct,
            "distinct_count": distinct_count,
            "sample_values": [str(x) for x in df[col].dropna().head(3).tolist()],
        }

    # 2. Duplicate Analysis
    exact_duplicates = int(df.duplicated().sum())
    key_cols = ["Order ID", "Product ID"] if "Order ID" in df.columns and "Product ID" in df.columns else []
    key_duplicates = int(df.duplicated(subset=key_cols).sum()) if key_cols else 0

    # 3. Date Integrity Analysis
    date_audit = {}
    if "Order Date" in df.columns and "Ship Date" in df.columns:
        order_dates = pd.to_datetime(df["Order Date"], errors="coerce")
        ship_dates = pd.to_datetime(df["Ship Date"], errors="coerce")
        invalid_order_dates = int(order_dates.isnull().sum())
        invalid_ship_dates = int(ship_dates.isnull().sum())
        date_inversions = int((ship_dates < order_dates).sum())
        lead_times = (ship_dates - order_dates).dt.days

        date_audit = {
            "order_date_range": {
                "min": str(order_dates.min()),
                "max": str(order_dates.max()),
                "invalid_format_count": invalid_order_dates,
            },
            "ship_date_range": {
                "min": str(ship_dates.min()),
                "max": str(ship_dates.max()),
                "invalid_format_count": invalid_ship_dates,
            },
            "date_inversions_ship_before_order": date_inversions,
            "lead_time_days_min": int(lead_times.min()) if not lead_times.empty else 0,
            "lead_time_days_max": int(lead_times.max()) if not lead_times.empty else 0,
            "lead_time_days_mean": round(float(lead_times.mean()), 2) if not lead_times.empty else 0.0,
        }

    # 4. Numeric Value Validity & Business Logic
    numeric_audit = {}
    for col in ["Sales", "Quantity", "Discount", "Profit"]:
        if col in df.columns:
            num_series = pd.to_numeric(df[col], errors="coerce")
            nan_count = int(num_series.isnull().sum())
            negative_count = int((num_series < 0).sum())
            zero_count = int((num_series == 0).sum())
            iqr_data = detect_outliers_iqr(num_series)
            numeric_audit[col] = {
                "min": round(float(num_series.min()), 4) if not num_series.empty else 0,
                "max": round(float(num_series.max()), 4) if not num_series.empty else 0,
                "mean": round(float(num_series.mean()), 4) if not num_series.empty else 0,
                "sum": round(float(num_series.sum()), 2) if not num_series.empty else 0,
                "non_numeric_nan_count": nan_count,
                "negative_value_count": negative_count,
                "zero_value_count": zero_count,
                "outlier_analysis": iqr_data,
            }

    # 5. Categorical Breakdown
    categorical_audit = {}
    for cat_col in ["Category", "Sub-Category", "Region", "Segment", "Ship Mode"]:
        if cat_col in df.columns:
            val_counts = df[cat_col].value_counts(dropna=False).to_dict()
            categorical_audit[cat_col] = {str(k): int(v) for k, v in val_counts.items()}

    profile = {
        "profile_name": profile_name,
        "summary": {
            "total_records": total_rows,
            "total_columns": total_cols,
            "exact_duplicate_rows": exact_duplicates,
            "order_product_composite_duplicates": key_duplicates,
        },
        "column_level_stats": column_stats,
        "date_audit": date_audit,
        "numeric_audit": numeric_audit,
        "categorical_audit": categorical_audit,
    }
    return profile


def run_pre_cleaning_profiling() -> Path:
    """Executes pre-cleaning profiling on data/raw/superstore_raw.csv and writes JSON."""
    root = get_project_root()
    raw_path = root / "data" / "raw" / "superstore_raw.csv"
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data file missing at: {raw_path}")

    df_raw = pd.read_csv(raw_path, encoding="latin1")
    profile = generate_profile(df_raw, profile_name="Pre-Cleaning Data Quality Profile")

    out_dir = root / "data" / "profiling"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "pre_cleaning_profile.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

    print("=" * 70)
    print("STAGE 3: PRE-CLEANING DATA PROFILING COMPLETED")
    print("=" * 70)
    print(f"Total Records Analyzed    : {profile['summary']['total_records']:,}")
    print(f"Total Columns Audited     : {profile['summary']['total_columns']}")
    print(f"Exact Duplicate Rows      : {profile['summary']['exact_duplicate_rows']}")
    print(f"Composite Key Duplicates  : {profile['summary']['order_product_composite_duplicates']}")
    print("\nMissing Values Audit:")
    for col, st in profile["column_level_stats"].items():
        if st["null_count"] > 0:
            print(f"  - {col:<15}: {st['null_count']} missing ({st['null_pct']}%)")
    print("\nDate Integrity Audit:")
    print(f"  - Order Dates: {profile['date_audit']['order_date_range']['min']} to {profile['date_audit']['order_date_range']['max']}")
    print(f"  - Date Inversions (Ship < Order): {profile['date_audit']['date_inversions_ship_before_order']}")
    print(f"  - Lead Time Range: {profile['date_audit']['lead_time_days_min']} to {profile['date_audit']['lead_time_days_max']} days")
    print("\nFinancial Value Integrity Audit:")
    for metric, st in profile["numeric_audit"].items():
        print(f"  - {metric:<10}: Min={st['min']:<10} Max={st['max']:<10} Sum={st['sum']:<15} NegativeCount={st['negative_value_count']}")
    print(f"\n[OUTPUT] Pre-cleaning profile saved to: {out_file}")
    return out_file


if __name__ == "__main__":
    run_pre_cleaning_profiling()
