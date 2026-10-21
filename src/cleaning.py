"""
Data Cleaning & Standardization Module
Business Performance Diagnosis & Decision Intelligence Platform

Preserves raw data untouched in data/raw/superstore_raw.csv.
Deconstructs bundled sheets (Orders, Regional Managers, Returns).
Logs every record treatment without silent drops.
Saves clean transactions to data/processed/clean_transactions.csv.
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def clean_dataset() -> dict:
    root = get_project_root()
    raw_path = root / "data" / "raw" / "superstore_raw.csv"
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data file missing at: {raw_path}")

    # Read raw data with Latin-1 encoding
    df_raw = pd.read_csv(raw_path, encoding="latin1")
    total_raw_rows = len(df_raw)

    print("=" * 70)
    print("STAGE 3: DATA CLEANING & RECONCILIATION")
    print("=" * 70)
    print(f"Total Raw Records Read: {total_raw_rows:,}")

    # 1. Structural Segmentation of Bundled Sheets
    # Rows 0-9993: Orders (9,994 rows)
    # Row 9994: Header 'Person/Region'
    # Rows 9995-9998: Regional Managers (4 rows)
    # Row 9999: Header 'Returned/Order ID'
    # Rows 10000-10799: Order Returns (800 rows)
    df_orders_raw = df_raw.iloc[:9994].copy()
    df_person_raw = df_raw.iloc[9995:9999].copy()
    df_returns_raw = df_raw.iloc[10000:10800].copy()

    # 2. Extract and Save Regional Managers
    df_managers = pd.DataFrame({
        "RegionalManager": df_person_raw["Row ID"].values,
        "Region": df_person_raw["Order ID"].values
    })
    managers_path = root / "data" / "processed" / "dim_regional_managers.csv"
    df_managers.to_csv(managers_path, index=False)
    print(f"[EXTRACT] Regional Managers Dimension : {len(df_managers)} rows saved to {managers_path.name}")

    # 3. Extract and Save Order Returns
    df_returns = pd.DataFrame({
        "ReturnedStatus": df_returns_raw["Row ID"].values,
        "OrderID": df_returns_raw["Order ID"].values
    })
    returns_path = root / "data" / "processed" / "order_returns.csv"
    df_returns.to_csv(returns_path, index=False)
    unique_returned_orders = set(df_returns["OrderID"].unique())
    print(f"[EXTRACT] Order Returns Table         : {len(df_returns)} records ({len(unique_returned_orders)} unique orders) saved to {returns_path.name}")

    # 4. Cleansing & Transforming Orders Transactions
    df_clean = df_orders_raw.copy()

    # 4.1 Type Casting Row ID
    df_clean["Row ID"] = df_clean["Row ID"].astype(int)

    # 4.2 Standardizing Dates
    df_clean["Order Date"] = pd.to_datetime(df_clean["Order Date"])
    df_clean["Ship Date"] = pd.to_datetime(df_clean["Ship Date"])
    df_clean["FulfillmentDays"] = (df_clean["Ship Date"] - df_clean["Order Date"]).dt.days

    # 4.3 Imputing Missing Postal Code (Burlington, Vermont)
    missing_postal_mask = df_clean["Postal Code"].isnull()
    imputed_postal_count = int(missing_postal_mask.sum())
    # Standard Burlington, VT zip code is 05408
    df_clean.loc[missing_postal_mask, "Postal Code"] = 5408.0
    # Format Postal Code as 5-digit zero-padded string
    df_clean["Postal Code"] = df_clean["Postal Code"].astype(int).astype(str).str.zfill(5)

    # 4.4 Numeric Normalization
    df_clean["Sales"] = pd.to_numeric(df_clean["Sales"]).round(4)
    df_clean["Quantity"] = pd.to_numeric(df_clean["Quantity"]).astype(int)
    df_clean["Discount"] = pd.to_numeric(df_clean["Discount"]).round(4)
    df_clean["Profit"] = pd.to_numeric(df_clean["Profit"]).round(4)

    # 4.5 Derived Business Metrics
    # COGS = Sales - Profit
    df_clean["COGS"] = (df_clean["Sales"] - df_clean["Profit"]).round(4)
    # Profit Margin % = Profit / Sales (handle Sales == 0 safely)
    df_clean["ProfitMarginPct"] = np.where(
        df_clean["Sales"] > 0,
        (df_clean["Profit"] / df_clean["Sales"]).round(6),
        0.0
    )
    # Unit Price = Sales / Quantity
    df_clean["UnitPrice"] = (df_clean["Sales"] / df_clean["Quantity"]).round(4)

    # 4.6 Flags and Diagnostic Brackets
    df_clean["IsLossMaking"] = df_clean["Profit"] < 0
    df_clean["IsReturned"] = df_clean["Order ID"].isin(unique_returned_orders)

    # Discount Brackets for Root-Cause Analysis
    conditions = [
        df_clean["Discount"] == 0.0,
        (df_clean["Discount"] > 0.0) & (df_clean["Discount"] <= 0.10),
        (df_clean["Discount"] > 0.10) & (df_clean["Discount"] <= 0.20),
        (df_clean["Discount"] > 0.20) & (df_clean["Discount"] <= 0.40),
        df_clean["Discount"] > 0.40
    ]
    choices = [
        "0% (No Discount)",
        "1-10% (Low)",
        "11-20% (Moderate)",
        "21-40% (High)",
        ">40% (Severe)"
    ]
    df_clean["DiscountBracket"] = np.select(conditions, choices, default="Unknown")

    # Format dates as ISO strings for clean CSV export
    df_clean["OrderDateFormatted"] = df_clean["Order Date"].dt.strftime("%Y-%m-%d")
    df_clean["ShipDateFormatted"] = df_clean["Ship Date"].dt.strftime("%Y-%m-%d")

    # 5. Save Clean Transactions
    out_clean_path = root / "data" / "processed" / "clean_transactions.csv"
    df_clean.to_csv(out_clean_path, index=False)
    print(f"[SUCCESS] Clean Transactions Saved   : {len(df_clean):,} records saved to {out_clean_path.name}")

    # 6. Detailed Traceability Log
    loss_making_count = int(df_clean["IsLossMaking"].sum())
    total_loss_amount = float(df_clean[df_clean["IsLossMaking"]]["Profit"].sum())
    returned_orders_count = int(df_clean["IsReturned"].sum())

    cleaning_log = {
        "raw_records_total": total_raw_rows,
        "orders_retained": len(df_clean),
        "regional_managers_extracted": len(df_managers),
        "returns_records_extracted": len(df_returns),
        "delimiter_header_rows_excluded": 2,  # Person/Region header and Returned/Order ID header
        "postal_codes_imputed": {
            "count": imputed_postal_count,
            "city": "Burlington",
            "state": "Vermont",
            "imputed_value": "05408"
        },
        "flags_and_diagnostics": {
            "loss_making_orders_count": loss_making_count,
            "loss_making_orders_pct": round((loss_making_count / len(df_clean)) * 100, 2),
            "total_negative_profit_amount": round(total_loss_amount, 2),
            "returned_order_lines_count": returned_orders_count,
            "returned_order_lines_pct": round((returned_orders_count / len(df_clean)) * 100, 2)
        },
        "reconciliation": {
            "raw_total": total_raw_rows,
            "accounted_for": len(df_clean) + len(df_managers) + len(df_returns) + 2,
            "discrepancy": total_raw_rows - (len(df_clean) + len(df_managers) + len(df_returns) + 2)
        }
    }

    log_path = root / "data" / "profiling" / "cleaning_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(cleaning_log, f, indent=2)

    print(f"[AUDIT] Full Cleaning Log Written To: {log_path.name}")
    print(f"[AUDIT] Total Input Rows Accounted For: {cleaning_log['reconciliation']['accounted_for']} / {total_raw_rows} (Discrepancy: {cleaning_log['reconciliation']['discrepancy']})")
    return cleaning_log


if __name__ == "__main__":
    clean_dataset()
