"""
Automated Test Suite: SQLite Data Warehouse & Reconciliation (Stage 5)
Business Performance Diagnosis & Decision Intelligence Platform
"""

import sqlite3
from pathlib import Path
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "sql" / "business_bi.db"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


@pytest.fixture(scope="session")
def db_conn():
    assert DB_PATH.exists(), f"Database missing at {DB_PATH}. Run sql/load_data.py first."
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def python_fact_orders():
    path = PROCESSED_DIR / "fact_orders.csv"
    assert path.exists()
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def python_fact_targets():
    path = PROCESSED_DIR / "fact_targets.csv"
    assert path.exists()
    return pd.read_csv(path)


class TestWarehouseSchemaAndIntegrity:
    """Verifies schema table counts, PRAGMA foreign keys, and zero FK violations."""

    def test_foreign_key_pragma_enabled(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute("PRAGMA foreign_keys;")
        assert cursor.fetchone()[0] == 1, "PRAGMA foreign_keys is NOT enabled!"

    def test_table_row_counts(self, db_conn):
        expected_counts = {
            "dim_ship_mode": 4,
            "dim_customer": 793,
            "dim_product": 1862,
            "dim_geography": 632,
            "dim_date": 1826,
            "fact_targets": 576,
            "fact_orders": 9994,
        }
        cursor = db_conn.cursor()
        for tbl, expected in expected_counts.items():
            cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
            actual = cursor.fetchone()[0]
            assert actual == expected, f"Table {tbl} row count mismatch: Expected {expected}, got {actual}"

    def test_zero_foreign_key_violations(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute("PRAGMA foreign_key_check;")
        violations = cursor.fetchall()
        assert len(violations) == 0, f"Found {len(violations)} foreign key violations: {violations}"

    def test_check_constraint_rejection(self, db_conn):
        """Verifies that SQLite CHECK constraints reject illegal negative sales or invalid foreign keys."""
        cursor = db_conn.cursor()
        with pytest.raises(sqlite3.IntegrityError):
            # Attempt to insert illegal negative sales record
            cursor.execute("""
                INSERT INTO fact_orders (
                    RowID, OrderID, OrderDateKey, ShipDateKey, CustomerID, ProductID,
                    GeographyID, ShipModeID, Sales, Quantity, Discount, Profit, COGS,
                    ProfitMarginPct, UnitPrice, FulfillmentDays, IsLossMaking, IsReturned, DiscountBracket
                ) VALUES (
                    99999, 'INVALID-TEST', 20150103, 20150107, 'CG-12520', 'FUR-BO-10001798',
                    1, 1, -100.0, 1, 0.0, 10.0, 90.0, 0.1, 100.0, 4, 0, 0, '0% (No Discount)'
                );
            """)


class TestAnalyticalBIViews:
    """Verifies that all 5 analytical views exist and return expected row counts."""

    def test_view_existence_and_row_counts(self, db_conn):
        expected_views = {
            "v_monthly_financials": 48,
            "v_target_variance_decomposition": 576,
            "v_regional_performance": 4,
            "v_subcategory_profitability": 17,
            "v_discount_bracket_margin_leakage": 5,
        }
        cursor = db_conn.cursor()
        for view_name, expected_rows in expected_views.items():
            cursor.execute(f"SELECT COUNT(*) FROM {view_name};")
            actual_rows = cursor.fetchone()[0]
            assert actual_rows == expected_rows, (
                f"View {view_name} row count mismatch: Expected {expected_rows}, got {actual_rows}"
            )


class TestPythonSQLReconciliation:
    """Cross-validates that SQL view outputs match Python calculations to the cent ($0.00 discrepancy)."""

    def test_grand_totals_reconciliation(self, db_conn, python_fact_orders):
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT
                ROUND(SUM(Sales), 2),
                ROUND(SUM(Profit), 2),
                ROUND(SUM(COGS), 2),
                SUM(Quantity),
                COUNT(*)
            FROM fact_orders;
        """)
        sql_sales, sql_profit, sql_cogs, sql_qty, sql_rows = cursor.fetchone()

        py_sales = round(float(python_fact_orders["Sales"].sum()), 2)
        py_profit = round(float(python_fact_orders["Profit"].sum()), 2)
        py_cogs = round(float(python_fact_orders["COGS"].sum()), 2)
        py_qty = int(python_fact_orders["Quantity"].sum())
        py_rows = len(python_fact_orders)

        assert abs(sql_sales - py_sales) < 0.01, f"Sales mismatch: SQL={sql_sales}, Py={py_sales}"
        assert abs(sql_profit - py_profit) < 0.01, f"Profit mismatch: SQL={sql_profit}, Py={py_profit}"
        assert abs(sql_cogs - py_cogs) < 0.01, f"COGS mismatch: SQL={sql_cogs}, Py={py_cogs}"
        assert sql_qty == py_qty, f"Quantity mismatch: SQL={sql_qty}, Py={py_qty}"
        assert sql_rows == py_rows, f"Row count mismatch: SQL={sql_rows}, Py={py_rows}"

    def test_regional_totals_reconciliation(self, db_conn, python_fact_orders):
        # Python Regional Totals
        geo_df = pd.read_csv(PROCESSED_DIR / "dim_geography.csv")
        merged = python_fact_orders.merge(geo_df, on="GeographyID")
        py_reg = merged.groupby("Region").agg({
            "Sales": lambda x: round(float(x.sum()), 2),
            "Profit": lambda x: round(float(x.sum()), 2)
        }).to_dict(orient="index")

        # SQL Regional Totals from View
        cursor = db_conn.cursor()
        cursor.execute("SELECT Region, TotalRevenue, TotalProfit FROM v_regional_performance ORDER BY Region;")
        sql_rows = cursor.fetchall()

        for region, sql_rev, sql_prof in sql_rows:
            py_rev = py_reg[region]["Sales"]
            py_prof = py_reg[region]["Profit"]
            assert abs(sql_rev - py_rev) < 0.01, f"Regional Revenue mismatch for {region}: SQL={sql_rev}, Py={py_rev}"
            assert abs(sql_prof - py_prof) < 0.01, f"Regional Profit mismatch for {region}: SQL={sql_prof}, Py={py_prof}"

    def test_target_totals_reconciliation(self, db_conn, python_fact_targets):
        cursor = db_conn.cursor()
        cursor.execute("SELECT ROUND(SUM(TargetRevenue), 2), ROUND(SUM(TargetProfit), 2) FROM fact_targets;")
        sql_t_rev, sql_t_prof = cursor.fetchone()

        py_t_rev = round(float(python_fact_targets["TargetRevenue"].sum()), 2)
        py_t_prof = round(float(python_fact_targets["TargetProfit"].sum()), 2)

        assert abs(sql_t_rev - py_t_rev) < 0.01, f"Target Revenue mismatch: SQL={sql_t_rev}, Py={py_t_rev}"
        assert abs(sql_t_prof - py_t_prof) < 0.01, f"Target Profit mismatch: SQL={sql_t_prof}, Py={py_t_prof}"
