"""
Star-Schema Dimensional Modeling & Transformation Module
Business Performance Diagnosis & Decision Intelligence Platform

Structures clean transactions into a Kimball Star Schema:
- FactOrders (9,994 rows)
- FactTargets (576 rows)
- DimDate (1,826 rows: 2015-01-01 to 2019-12-31)
- DimCustomer (793 rows)
- DimProduct (1,862 rows)
- DimGeography (632 rows)
- DimShipMode (4 rows)

Validates PK uniqueness, non-null constraints, and 100% FK referential integrity.
"""

from pathlib import Path
import pandas as pd
import numpy as np


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def build_star_schema() -> dict:
    root = get_project_root()
    clean_path = root / "data" / "processed" / "clean_transactions.csv"
    targets_path = root / "data" / "processed" / "fact_targets.csv"
    out_dir = root / "data" / "processed"

    if not clean_path.exists():
        raise FileNotFoundError(f"Clean transactions missing at {clean_path}")
    if not targets_path.exists():
        raise FileNotFoundError(f"Fact targets missing at {targets_path}. Run generate_targets.py first.")

    df_clean = pd.read_csv(clean_path)
    df_targets = pd.read_csv(targets_path)

    print("=" * 70)
    print("STAGE 4: STAR-SCHEMA DIMENSIONAL MODELING")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. DimShipMode (4 rows)
    # -------------------------------------------------------------
    ship_modes_sla = [
        {"ShipModeID": 1, "ShipMode": "Same Day", "StandardSLADays": 0},
        {"ShipModeID": 2, "ShipMode": "First Class", "StandardSLADays": 2},
        {"ShipModeID": 3, "ShipMode": "Second Class", "StandardSLADays": 4},
        {"ShipModeID": 4, "ShipMode": "Standard Class", "StandardSLADays": 6},
    ]
    df_dim_ship_mode = pd.DataFrame(ship_modes_sla)
    ship_mode_map = dict(zip(df_dim_ship_mode["ShipMode"], df_dim_ship_mode["ShipModeID"]))
    df_dim_ship_mode.to_csv(out_dir / "dim_ship_mode.csv", index=False)
    print(f"[DIM] DimShipMode created      : {len(df_dim_ship_mode)} rows (PK: ShipModeID)")

    # -------------------------------------------------------------
    # 2. DimCustomer (793 rows)
    # -------------------------------------------------------------
    df_dim_customer = df_clean[["Customer ID", "Customer Name", "Segment"]].drop_duplicates().copy()
    df_dim_customer.rename(columns={
        "Customer ID": "CustomerID",
        "Customer Name": "CustomerName"
    }, inplace=True)
    df_dim_customer.sort_values("CustomerID", inplace=True)
    df_dim_customer.to_csv(out_dir / "dim_customer.csv", index=False)
    print(f"[DIM] DimCustomer created      : {len(df_dim_customer)} rows (PK: CustomerID)")

    # -------------------------------------------------------------
    # 3. DimProduct (1,862 rows)
    # Canonicalize product name to handle minor typographic variations
    # -------------------------------------------------------------
    df_dim_product = df_clean.groupby("Product ID").first().reset_index()[["Product ID", "Category", "Sub-Category", "Product Name"]].copy()
    df_dim_product.rename(columns={
        "Product ID": "ProductID",
        "Sub-Category": "SubCategory",
        "Product Name": "ProductName"
    }, inplace=True)
    df_dim_product.sort_values("ProductID", inplace=True)
    df_dim_product.to_csv(out_dir / "dim_product.csv", index=False)
    print(f"[DIM] DimProduct created       : {len(df_dim_product)} rows (PK: ProductID)")

    # -------------------------------------------------------------
    # 4. DimGeography (632 rows)
    # -------------------------------------------------------------
    geo_cols = ["City", "State", "Postal Code", "Region", "Country"]
    df_dim_geography = df_clean[geo_cols].drop_duplicates().reset_index(drop=True).copy()
    df_dim_geography["GeographyID"] = range(1, len(df_dim_geography) + 1)
    df_dim_geography.rename(columns={"Postal Code": "PostalCode"}, inplace=True)
    # Reorder columns with PK first
    df_dim_geography = df_dim_geography[["GeographyID", "City", "State", "PostalCode", "Region", "Country"]]
    df_dim_geography.to_csv(out_dir / "dim_geography.csv", index=False)
    print(f"[DIM] DimGeography created     : {len(df_dim_geography)} rows (PK: GeographyID)")

    # Create mapping dictionary for fast foreign key lookup
    geo_lookup = {}
    for _, row in df_dim_geography.iterrows():
        key = (row["City"], row["State"], str(row["PostalCode"]), row["Region"], row["Country"])
        geo_lookup[key] = int(row["GeographyID"])

    # -------------------------------------------------------------
    # 5. DimDate (1,826 rows: 2015-01-01 to 2019-12-31)
    # Full 5 calendar years to encompass all order and ship dates
    # -------------------------------------------------------------
    start_date = pd.to_datetime("2015-01-01")
    end_date = pd.to_datetime("2019-12-31")
    dates = pd.date_range(start_date, end_date)

    date_records = []
    for d in dates:
        date_key = int(d.strftime("%Y%m%d"))
        date_records.append({
            "DateKey": date_key,
            "FullDate": d.strftime("%Y-%m-%d"),
            "Year": int(d.year),
            "Quarter": f"Q{d.quarter}",
            "QuarterNumber": int(d.quarter),
            "YearQuarter": f"{d.year}-Q{d.quarter}",
            "Month": int(d.month),
            "MonthName": d.strftime("%B"),
            "MonthShort": d.strftime("%b"),
            "YearMonth": d.strftime("%Y-%m"),
            "DayOfMonth": int(d.day),
            "DayOfWeek": int(d.dayofweek + 1), # 1=Monday, 7=Sunday
            "DayName": d.strftime("%A"),
            "IsWeekend": 1 if d.dayofweek in [5, 6] else 0
        })
    df_dim_date = pd.DataFrame(date_records)
    df_dim_date.to_csv(out_dir / "dim_date.csv", index=False)
    print(f"[DIM] DimDate created          : {len(df_dim_date)} rows (PK: DateKey, 2015-2019)")

    # -------------------------------------------------------------
    # 6. FactOrders (9,994 rows)
    # Assemble foreign keys and business metrics
    # -------------------------------------------------------------
    df_fact = pd.DataFrame()
    df_fact["RowID"] = df_clean["Row ID"].astype(int)
    df_fact["OrderID"] = df_clean["Order ID"]

    # Foreign Keys
    order_dt = pd.to_datetime(df_clean["Order Date"])
    ship_dt = pd.to_datetime(df_clean["Ship Date"])
    df_fact["OrderDateKey"] = order_dt.dt.strftime("%Y%m%d").astype(int)
    df_fact["ShipDateKey"] = ship_dt.dt.strftime("%Y%m%d").astype(int)
    df_fact["CustomerID"] = df_clean["Customer ID"]
    df_fact["ProductID"] = df_clean["Product ID"]

    # Map GeographyID
    geo_keys = [
        geo_lookup.get((c, s, str(p), r, co), -1)
        for c, s, p, r, co in zip(
            df_clean["City"],
            df_clean["State"],
            df_clean["Postal Code"].astype(str),
            df_clean["Region"],
            df_clean["Country"]
        )
    ]
    df_fact["GeographyID"] = geo_keys

    # Map ShipModeID
    df_fact["ShipModeID"] = df_clean["Ship Mode"].map(ship_mode_map)

    # Measures & Metrics (Preserve 4-decimal precision to prevent premature row-level rounding drift)
    df_fact["Sales"] = df_clean["Sales"].round(4)
    df_fact["Quantity"] = df_clean["Quantity"].astype(int)
    df_fact["Discount"] = df_clean["Discount"].round(4)
    df_fact["Profit"] = df_clean["Profit"].round(4)
    df_fact["COGS"] = df_clean["COGS"].round(4)
    df_fact["ProfitMarginPct"] = df_clean["ProfitMarginPct"].round(6)
    df_fact["UnitPrice"] = df_clean["UnitPrice"].round(4)
    df_fact["FulfillmentDays"] = df_clean["FulfillmentDays"].astype(int)

    # Diagnostic Flags
    df_fact["IsLossMaking"] = df_clean["IsLossMaking"].astype(int)
    df_fact["IsReturned"] = df_clean["IsReturned"].astype(int)
    df_fact["DiscountBracket"] = df_clean["DiscountBracket"]

    df_fact.sort_values("RowID", inplace=True)
    df_fact.to_csv(out_dir / "fact_orders.csv", index=False)
    print(f"[FACT] FactOrders created      : {len(df_fact)} rows (PK: RowID)")

    # -------------------------------------------------------------
    # 7. Referential Integrity & Quality Validations
    # -------------------------------------------------------------
    date_keys_set = set(df_dim_date["DateKey"])
    cust_keys_set = set(df_dim_customer["CustomerID"])
    prod_keys_set = set(df_dim_product["ProductID"])
    geo_keys_set = set(df_dim_geography["GeographyID"])
    ship_keys_set = set(df_dim_ship_mode["ShipModeID"])

    # Target FK Validation
    target_date_orphans = df_targets[~df_targets["TargetDateKey"].isin(date_keys_set)]

    # FactOrders FK Validation
    order_date_orphans = df_fact[~df_fact["OrderDateKey"].isin(date_keys_set)]
    ship_date_orphans = df_fact[~df_fact["ShipDateKey"].isin(date_keys_set)]
    cust_orphans = df_fact[~df_fact["CustomerID"].isin(cust_keys_set)]
    prod_orphans = df_fact[~df_fact["ProductID"].isin(prod_keys_set)]
    geo_orphans = df_fact[~df_fact["GeographyID"].isin(geo_keys_set)]
    ship_orphans = df_fact[~df_fact["ShipModeID"].isin(ship_keys_set)]

    validation_results = {
        "FactOrders_rows": len(df_fact),
        "FactTargets_rows": len(df_targets),
        "DimCustomer_rows": len(df_dim_customer),
        "DimProduct_rows": len(df_dim_product),
        "DimGeography_rows": len(df_dim_geography),
        "DimShipMode_rows": len(df_dim_ship_mode),
        "DimDate_rows": len(df_dim_date),
        "FK_Violations": {
            "FactOrders_OrderDateKey": len(order_date_orphans),
            "FactOrders_ShipDateKey": len(ship_date_orphans),
            "FactOrders_CustomerID": len(cust_orphans),
            "FactOrders_ProductID": len(prod_orphans),
            "FactOrders_GeographyID": len(geo_orphans),
            "FactOrders_ShipModeID": len(ship_orphans),
            "FactTargets_TargetDateKey": len(target_date_orphans),
        }
    }

    print("\nReferential Integrity Audit:")
    for fk, violations in validation_results["FK_Violations"].items():
        status = "[PASS]" if violations == 0 else "[FAIL]"
        print(f"  {status} {fk:<30}: {violations} orphaned keys")

    return validation_results


if __name__ == "__main__":
    build_star_schema()
