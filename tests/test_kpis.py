"""
Automated Test Suite: KPI Engine, Edge Cases & Python-SQL Reconciliation (Stage 6)
Business Performance Diagnosis & Decision Intelligence Platform
"""

import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.kpi_engine import (
    safe_divide,
    calculate_portfolio_kpis,
    calculate_regional_kpis,
    calculate_subcategory_kpis,
    calculate_discount_bracket_kpis
)
from src.diagnosis import (
    diagnose_target_variance,
    diagnose_discount_margin_association,
    diagnose_loss_making_transactions,
    diagnose_chronic_underperformers
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DB_PATH = PROJECT_ROOT / "sql" / "business_bi.db"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"


@pytest.fixture(scope="session")
def fact_orders():
    return pd.read_csv(PROCESSED_DIR / "fact_orders.csv")


@pytest.fixture(scope="session")
def dim_geo():
    return pd.read_csv(PROCESSED_DIR / "dim_geography.csv")


@pytest.fixture(scope="session")
def dim_prod():
    return pd.read_csv(PROCESSED_DIR / "dim_product.csv")


@pytest.fixture(scope="session")
def fact_targets():
    return pd.read_csv(PROCESSED_DIR / "fact_targets.csv")


@pytest.fixture(scope="session")
def dim_date():
    return pd.read_csv(PROCESSED_DIR / "dim_date.csv")


class TestSafeDivideAndEdgeCases:
    """Tests zero-denominators, missing values, empty inputs, and boundary conditions."""

    def test_safe_divide_zero_denominator(self):
        assert safe_divide(100.0, 0.0) == 0.0
        assert safe_divide(100.0, 0) == 0.0

    def test_safe_divide_nan_inf(self):
        assert safe_divide(100.0, np.nan) == 0.0
        assert safe_divide(100.0, np.inf) == 0.0
        assert safe_divide(np.nan, 100.0) == 0.0

    def test_safe_divide_normal(self):
        assert safe_divide(100.0, 4.0) == 25.0

    def test_empty_dataframe_portfolio_kpis(self):
        empty_df = pd.DataFrame()
        res = calculate_portfolio_kpis(empty_df)
        assert res["TotalOrderLines"] == 0
        assert res["TotalRevenue"] == 0.0
        assert res["GrossMarginPct"] == 0.0
        assert res["LossMakingOrderLines"] == 0

    def test_zero_revenue_zero_denominator_kpis(self):
        zero_rev_df = pd.DataFrame({
            "Sales": [0.0],
            "Profit": [0.0],
            "COGS": [0.0],
            "Quantity": [1],
            "OrderID": ["TEST-1"],
            "IsLossMaking": [0],
            "IsReturned": [0],
            "FulfillmentDays": [2]
        })
        res = calculate_portfolio_kpis(zero_rev_df)
        assert res["GrossMarginPct"] == 0.0
        assert res["AvgOrderValue"] == 0.0

    def test_negative_profit_handling(self):
        loss_df = pd.DataFrame({
            "Sales": [100.0],
            "Profit": [-50.0],
            "COGS": [150.0],
            "Quantity": [2],
            "OrderID": ["TEST-LOSS"],
            "IsLossMaking": [1],
            "IsReturned": [0],
            "FulfillmentDays": [3]
        })
        res = calculate_portfolio_kpis(loss_df)
        assert res["GrossMarginPct"] == -0.5
        assert res["LossMakingOrderLines"] == 1
        assert res["TotalCashLeakageDollar"] == 50.0


class TestPortfolioKPIActualValues:
    """Verifies that Python KPI Engine produces exact verified numbers on the actual dataset."""

    def test_portfolio_kpis_on_actual_data(self, fact_orders):
        res = calculate_portfolio_kpis(fact_orders)
        assert res["TotalOrderLines"] == 9994
        assert res["DistinctOrders"] == 5009
        assert abs(res["TotalRevenue"] - 2297200.86) < 0.01
        assert abs(res["TotalProfit"] - 286397.02) < 0.01
        assert res["TotalQuantity"] == 37873
        assert res["LossMakingOrderLines"] == 1871
        assert abs(res["TotalCashLeakageDollar"] - 156131.29) < 0.01
        assert abs(res["GrossMarginPct"] - 0.1247) < 0.0001


class TestReconciliationWithSQLViews:
    """Verifies Python functions match SQLite analytical views within financial tolerance (< $0.01)."""

    def test_regional_kpis_match_sql_view(self, fact_orders, dim_geo):
        py_reg = calculate_regional_kpis(fact_orders, dim_geo).set_index("Region")

        conn = sqlite3.connect(DB_PATH)
        sql_reg = pd.read_sql_query("SELECT * FROM v_regional_performance", conn).set_index("Region")
        conn.close()

        for region in ["Central", "East", "South", "West"]:
            py_row = py_reg.loc[region]
            sql_row = sql_reg.loc[region]

            assert abs(py_row["TotalRevenue"] - sql_row["TotalRevenue"]) < 0.01
            assert abs(py_row["TotalProfit"] - sql_row["TotalProfit"]) < 0.01
            assert abs(py_row["GrossMarginPct"] - sql_row["GrossMarginPct"]) < 0.001
            assert py_row["LossMakingTransactions"] == sql_row["LossMakingTransactions"]
            assert abs(py_row["CashLeakageDollar"] - sql_row["CashLeakageDollar"]) < 0.01

    def test_subcategory_kpis_match_sql_view(self, fact_orders, dim_prod):
        py_subcat = calculate_subcategory_kpis(fact_orders, dim_prod).set_index("SubCategory")

        conn = sqlite3.connect(DB_PATH)
        sql_subcat = pd.read_sql_query("SELECT * FROM v_subcategory_profitability", conn).set_index("SubCategory")
        conn.close()

        assert len(py_subcat) == 17
        assert len(sql_subcat) == 17

        for subcat in py_subcat.index:
            py_row = py_subcat.loc[subcat]
            sql_row = sql_subcat.loc[subcat]
            assert abs(py_row["TotalRevenue"] - sql_row["TotalRevenue"]) < 0.01
            assert abs(py_row["TotalProfit"] - sql_row["TotalProfit"]) < 0.01


class TestDiagnosticEngineAndCharts:
    """Verifies diagnostic engine logic and existence of generated chart files."""

    def test_statistical_correlation_bounds(self, fact_orders):
        diag = diagnose_discount_margin_association(fact_orders)
        assert diag["PearsonCorrelation"] < -0.20
        assert diag["SpearmanCorrelation"] < -0.30

    def test_loss_making_profiling(self, fact_orders, dim_geo, dim_prod):
        loss_diag = diagnose_loss_making_transactions(fact_orders, dim_geo, dim_prod)
        assert loss_diag["TotalLossMakingTransactions"] == 1871
        assert abs(loss_diag["TotalCashLeakageDollar"] - 156131.29) < 0.01
        assert loss_diag["AvgDiscountLossMakingOrders"] > loss_diag["AvgDiscountProfitableOrders"]

    def test_chronic_subcategories_identified(self, fact_orders, dim_prod):
        chronic = diagnose_chronic_underperformers(fact_orders, dim_prod)
        assert chronic["ChronicLossMakingSubCategoriesCount"] == 3
        subcats = {x["SubCategory"] for x in chronic["ChronicLossMakingSubCategories"]}
        assert subcats == {"Tables", "Bookcases", "Supplies"}

    def test_chart_files_generated_and_non_empty(self):
        expected_charts = [
            "pareto_revenue_by_subcategory.png",
            "profit_margin_vs_discount_scatter.png",
            "regional_target_attainment_waterfall.png",
            "fulfillment_sla_adherence_breakdown.png"
        ]
        for chart_name in expected_charts:
            chart_file = FIGURES_DIR / chart_name
            assert chart_file.exists(), f"Chart {chart_name} missing at {chart_file}"
            file_size_kb = chart_file.stat().st_size / 1024.0
            assert file_size_kb > 50, f"Chart {chart_name} unexpectedly small ({file_size_kb:.1f} KB)"
