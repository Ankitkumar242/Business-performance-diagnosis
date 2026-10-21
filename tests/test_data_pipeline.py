"""
Automated Test Suite: Data Pipeline & Quality Validation (Stage 3)
Business Performance Diagnosis & Decision Intelligence Platform
"""

import hashlib
import json
from pathlib import Path
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "superstore_raw.csv"
CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "clean_transactions.csv"
MANAGERS_PATH = PROJECT_ROOT / "data" / "processed" / "dim_regional_managers.csv"
RETURNS_PATH = PROJECT_ROOT / "data" / "processed" / "order_returns.csv"
CLEANING_LOG_PATH = PROJECT_ROOT / "data" / "profiling" / "cleaning_log.json"

EXPECTED_RAW_SHA256 = "af443ca30d732c886f7a1d603f9492f98e9a88c268d47cbc146fe758b1f5d65d"


@pytest.fixture(scope="session")
def raw_df():
    assert RAW_PATH.exists(), f"Raw data file missing at {RAW_PATH}"
    return pd.read_csv(RAW_PATH, encoding="latin1")


@pytest.fixture(scope="session")
def clean_df():
    assert CLEAN_PATH.exists(), f"Clean transactions file missing at {CLEAN_PATH}"
    return pd.read_csv(CLEAN_PATH)


class TestRawDataIntegrity:
    """Verifies that the raw input dataset is preserved, untouched, and authentic."""

    def test_raw_file_immutability_checksum(self):
        sha256 = hashlib.sha256()
        with open(RAW_PATH, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        actual_hash = sha256.hexdigest()
        assert actual_hash == EXPECTED_RAW_SHA256, (
            f"Raw file was unexpectedly modified! Expected {EXPECTED_RAW_SHA256}, got {actual_hash}"
        )

    def test_raw_record_volume(self, raw_df):
        assert len(raw_df) == 10800, f"Expected 10,800 raw rows, got {len(raw_df)}"
        assert len(raw_df.columns) == 21, f"Expected 21 raw columns, got {len(raw_df.columns)}"


class TestCleaningAndAccountability:
    """Verifies that no records were silently dropped and all sub-sheets were preserved."""

    def test_complete_row_accountability_zero_drops(self, clean_df):
        assert MANAGERS_PATH.exists()
        assert RETURNS_PATH.exists()
        assert CLEANING_LOG_PATH.exists()

        df_mgr = pd.read_csv(MANAGERS_PATH)
        df_ret = pd.read_csv(RETURNS_PATH)
        with open(CLEANING_LOG_PATH, "r", encoding="utf-8") as f:
            log = json.load(f)

        assert len(clean_df) == 9994
        assert len(df_mgr) == 4
        assert len(df_ret) == 800
        # 9994 orders + 4 managers + 800 returns + 2 delimiter headers = 10,800
        total_accounted = len(clean_df) + len(df_mgr) + len(df_ret) + 2
        assert total_accounted == 10800
        assert log["reconciliation"]["discrepancy"] == 0

    def test_zero_null_values_in_clean_dataset(self, clean_df):
        null_counts = clean_df.isnull().sum()
        total_nulls = int(null_counts.sum())
        assert total_nulls == 0, f"Clean dataset contains unexpected nulls:\n{null_counts[null_counts > 0]}"

    def test_postal_code_imputation_burlington(self, clean_df):
        burlington_records = clean_df[clean_df["City"] == "Burlington"]
        assert len(burlington_records) > 0
        # Check that Vermont records have valid 5-digit zip code '05408'
        vt_burlington = burlington_records[burlington_records["State"] == "Vermont"]
        assert len(vt_burlington) == 11
        for zip_val in vt_burlington["Postal Code"]:
            assert str(zip_val) == "05408" or str(zip_val) == "5408"

    def test_primary_key_uniqueness(self, clean_df):
        assert clean_df["Row ID"].nunique() == len(clean_df), "Primary key Row ID contains duplicates!"


class TestTemporalAndFinancialInvariants:
    """Verifies business logic, chronological rules, and financial reconciliation."""

    def test_zero_date_inversions(self, clean_df):
        order_dates = pd.to_datetime(clean_df["Order Date"])
        ship_dates = pd.to_datetime(clean_df["Ship Date"])
        inversions = (ship_dates < order_dates).sum()
        assert inversions == 0, f"Detected {inversions} date inversions where Ship Date < Order Date!"

    def test_lead_time_bounds(self, clean_df):
        assert (clean_df["FulfillmentDays"] >= 0).all()
        assert (clean_df["FulfillmentDays"] <= 14).all()

    def test_sales_financial_reconciliation(self, raw_df, clean_df):
        raw_sales_sum = round(float(pd.to_numeric(raw_df["Sales"], errors="coerce").dropna().sum()), 2)
        clean_sales_sum = round(float(clean_df["Sales"].sum()), 2)
        variance = abs(clean_sales_sum - raw_sales_sum)
        assert variance < 0.01, f"Sales total mismatch! Raw={raw_sales_sum}, Clean={clean_sales_sum}"

    def test_profit_financial_reconciliation(self, raw_df, clean_df):
        raw_profit_sum = round(float(pd.to_numeric(raw_df["Profit"], errors="coerce").dropna().sum()), 2)
        clean_profit_sum = round(float(clean_df["Profit"].sum()), 2)
        variance = abs(clean_profit_sum - raw_profit_sum)
        assert variance < 0.01, f"Profit total mismatch! Raw={raw_profit_sum}, Clean={clean_profit_sum}"

    def test_cogs_mathematical_identity(self, clean_df):
        # Identity: COGS + Profit == Sales (Tolerance: 0.001 to handle IEEE 754 float epsilon)
        diff = (clean_df["COGS"] + clean_df["Profit"] - clean_df["Sales"]).abs()
        max_diff = float(diff.max())
        assert max_diff < 0.001, f"COGS + Profit != Sales violation! Max diff = {max_diff}"

    def test_discount_brackets_coverage(self, clean_df):
        expected_brackets = {
            "0% (No Discount)",
            "1-10% (Low)",
            "11-20% (Moderate)",
            "21-40% (High)",
            ">40% (Severe)"
        }
        actual_brackets = set(clean_df["DiscountBracket"].unique())
        assert actual_brackets.issubset(expected_brackets)
        assert "Unknown" not in actual_brackets

    def test_diagnostic_flags_presence(self, clean_df):
        assert "IsLossMaking" in clean_df.columns
        assert "IsReturned" in clean_df.columns
        loss_count = int(clean_df["IsLossMaking"].sum())
        assert loss_count == 1871  # Exactly 1,871 loss-making transactions in Superstore
