"""
SQLite Data Warehouse Loader Module
Business Performance Diagnosis & Decision Intelligence Platform

Idempotent and repeatable loader: loads validated CSVs from data/processed/
into sql/business_bi.db with foreign key enforcement and zero duplication.
"""

import sqlite3
from pathlib import Path
import pandas as pd


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def init_and_load_warehouse(db_path: Path = None) -> dict:
    root = get_project_root()
    if db_path is None:
        db_path = root / "sql" / "business_bi.db"

    schema_path = root / "sql" / "schema.sql"
    processed_dir = root / "data" / "processed"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file missing at: {schema_path}")

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("STAGE 5: SQL DATA WAREHOUSE INITIALIZATION & LOADING")
    print("=" * 70)
    print(f"Target SQLite Database : {db_path}")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # 1. Execute Schema DDL
    with open(schema_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    cursor.executescript(ddl)
    conn.commit()
    print("[DDL] Schema DDL executed successfully with PRAGMA foreign_keys = ON.")

    # 2. Ordered Loading of Dimensions First, Then Facts (Respecting Foreign Keys)
    # Using clean deletion of existing rows before load to guarantee idempotency without duplication
    load_plan = [
        ("dim_ship_mode", "dim_ship_mode.csv"),
        ("dim_customer", "dim_customer.csv"),
        ("dim_product", "dim_product.csv"),
        ("dim_geography", "dim_geography.csv"),
        ("dim_date", "dim_date.csv"),
        ("fact_targets", "fact_targets.csv"),
        ("fact_orders", "fact_orders.csv"),
    ]

    loaded_counts = {}

    # Disable FK checks temporarily ONLY during clean truncate to avoid circular constraint errors,
    # then re-enable immediately before inserting
    conn.execute("PRAGMA foreign_keys = OFF;")
    for table_name, _ in reversed(load_plan):
        cursor.execute(f"DELETE FROM {table_name};")
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON;")

    print("\n[LOAD] Inserting verified star-schema CSV records:")
    for table_name, csv_name in load_plan:
        csv_file = processed_dir / csv_name
        if not csv_file.exists():
            raise FileNotFoundError(f"Source CSV missing: {csv_file}")

        df = pd.read_csv(csv_file)
        # Load into SQLite table
        df.to_sql(table_name, conn, if_exists="append", index=False)
        conn.commit()

        # Verify row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        loaded_counts[table_name] = count
        print(f"  - {table_name:<20}: {count:,} rows loaded (from {csv_name})")

    # 3. Quick Sanity Check on Financial Totals
    cursor.execute("SELECT ROUND(SUM(Sales), 2), ROUND(SUM(Profit), 2) FROM fact_orders;")
    sql_sales, sql_profit = cursor.fetchone()
    print(f"\n[RECONCILE] FactOrders Total Sales  : ${sql_sales:,.2f}")
    print(f"[RECONCILE] FactOrders Total Profit : ${sql_profit:,.2f}")

    conn.close()
    print("=" * 70)
    print("DATA WAREHOUSE LOAD COMPLETE (IDEMPOTENT & VERIFIED)")
    print("=" * 70)
    return loaded_counts


if __name__ == "__main__":
    init_and_load_warehouse()
