"""
Automated Test Suite: Star Schema & Dimensional Integrity (Stage 4)
Business Performance Diagnosis & Decision Intelligence Platform
"""

from pathlib import Path
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


@pytest.fixture(scope="session")
def fact_orders():
    path = PROCESSED_DIR / "fact_orders.csv"
    assert path.exists(), f"fact_orders.csv missing at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def fact_targets():
    path = PROCESSED_DIR / "fact_targets.csv"
    assert path.exists(), f"fact_targets.csv missing at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def dim_customer():
    path = PROCESSED_DIR / "dim_customer.csv"
    assert path.exists(), f"dim_customer.csv missing at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def dim_product():
    path = PROCESSED_DIR / "dim_product.csv"
    assert path.exists(), f"dim_product.csv missing at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def dim_geography():
    path = PROCESSED_DIR / "dim_geography.csv"
    assert path.exists(), f"dim_geography.csv missing at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def dim_ship_mode():
    path = PROCESSED_DIR / "dim_ship_mode.csv"
    assert path.exists(), f"dim_ship_mode.csv missing at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def dim_date():
    path = PROCESSED_DIR / "dim_date.csv"
    assert path.exists(), f"dim_date.csv missing at {path}"
    return pd.read_csv(path)


class TestStarSchemaRowCounts:
    """Verifies that actual dimensional counts match verified data, not assumptions."""

    def test_fact_orders_row_count(self, fact_orders):
        assert len(fact_orders) == 9994, f"Expected 9,994 orders, got {len(fact_orders)}"

    def test_fact_targets_row_count(self, fact_targets):
        assert len(fact_targets) == 576, f"Expected 576 targets (48 mos x 4 reg x 3 cat), got {len(fact_targets)}"

    def test_dim_customer_actual_count(self, dim_customer):
        assert len(dim_customer) == 793, f"Expected exactly 793 unique customers, got {len(dim_customer)}"

    def test_dim_product_actual_count(self, dim_product):
        assert len(dim_product) == 1862, f"Expected exactly 1,862 unique products, got {len(dim_product)}"

    def test_dim_geography_actual_count(self, dim_geography):
        assert len(dim_geography) == 632, f"Expected exactly 632 unique geographic nodes, got {len(dim_geography)}"

    def test_dim_ship_mode_count(self, dim_ship_mode):
        assert len(dim_ship_mode) == 4, f"Expected 4 ship modes, got {len(dim_ship_mode)}"

    def test_dim_date_coverage_count(self, dim_date):
        assert len(dim_date) == 1826, f"Expected 1,826 days (5 full years 2015-2019), got {len(dim_date)}"


class TestPrimaryKeyUniqueness:
    """Verifies primary key uniqueness across all fact and dimension tables."""

    def test_fact_orders_pk(self, fact_orders):
        assert fact_orders["RowID"].nunique() == len(fact_orders)

    def test_fact_targets_pk(self, fact_targets):
        assert fact_targets["TargetID"].nunique() == len(fact_targets)

    def test_dim_customer_pk(self, dim_customer):
        assert dim_customer["CustomerID"].nunique() == len(dim_customer)

    def test_dim_product_pk(self, dim_product):
        assert dim_product["ProductID"].nunique() == len(dim_product)

    def test_dim_geography_pk(self, dim_geography):
        assert dim_geography["GeographyID"].nunique() == len(dim_geography)

    def test_dim_ship_mode_pk(self, dim_ship_mode):
        assert dim_ship_mode["ShipModeID"].nunique() == len(dim_ship_mode)

    def test_dim_date_pk(self, dim_date):
        assert dim_date["DateKey"].nunique() == len(dim_date)


class TestReferentialIntegrityForeignKeys:
    """Verifies 100% referential integrity with zero orphaned foreign keys."""

    def test_fk_fact_orders_order_date(self, fact_orders, dim_date):
        valid_keys = set(dim_date["DateKey"])
        orphans = fact_orders[~fact_orders["OrderDateKey"].isin(valid_keys)]
        assert len(orphans) == 0, f"Found {len(orphans)} orphaned OrderDateKey values!"

    def test_fk_fact_orders_ship_date(self, fact_orders, dim_date):
        valid_keys = set(dim_date["DateKey"])
        orphans = fact_orders[~fact_orders["ShipDateKey"].isin(valid_keys)]
        assert len(orphans) == 0, f"Found {len(orphans)} orphaned ShipDateKey values!"

    def test_fk_fact_orders_customer(self, fact_orders, dim_customer):
        valid_keys = set(dim_customer["CustomerID"])
        orphans = fact_orders[~fact_orders["CustomerID"].isin(valid_keys)]
        assert len(orphans) == 0, f"Found {len(orphans)} orphaned CustomerID values!"

    def test_fk_fact_orders_product(self, fact_orders, dim_product):
        valid_keys = set(dim_product["ProductID"])
        orphans = fact_orders[~fact_orders["ProductID"].isin(valid_keys)]
        assert len(orphans) == 0, f"Found {len(orphans)} orphaned ProductID values!"

    def test_fk_fact_orders_geography(self, fact_orders, dim_geography):
        valid_keys = set(dim_geography["GeographyID"])
        orphans = fact_orders[~fact_orders["GeographyID"].isin(valid_keys)]
        assert len(orphans) == 0, f"Found {len(orphans)} orphaned GeographyID values!"

    def test_fk_fact_orders_ship_mode(self, fact_orders, dim_ship_mode):
        valid_keys = set(dim_ship_mode["ShipModeID"])
        orphans = fact_orders[~fact_orders["ShipModeID"].isin(valid_keys)]
        assert len(orphans) == 0, f"Found {len(orphans)} orphaned ShipModeID values!"

    def test_fk_fact_targets_date(self, fact_targets, dim_date):
        valid_keys = set(dim_date["DateKey"])
        orphans = fact_targets[~fact_targets["TargetDateKey"].isin(valid_keys)]
        assert len(orphans) == 0, f"Found {len(orphans)} orphaned TargetDateKey values!"


class TestGovernanceAndFinancialIntegrity:
    """Verifies synthetic target labeling and financial reconciliation."""

    def test_synthetic_target_explicit_labeling(self, fact_targets):
        labels = fact_targets["TargetType"].unique()
        assert len(labels) == 1
        assert labels[0] == "Synthetic Managerial Budget Target"

    def test_fact_orders_sales_profit_totals(self, fact_orders):
        total_sales = round(float(fact_orders["Sales"].sum()), 2)
        total_profit = round(float(fact_orders["Profit"].sum()), 2)
        assert abs(total_sales - 2297200.86) < 0.01, f"Sales total deviation: {total_sales}"
        assert abs(total_profit - 286397.02) < 0.01, f"Profit total deviation: {total_profit}"
