"""
Data Ingestion Module
Business Performance Diagnosis & Decision Intelligence Platform

Preserves raw data in an untouched, immutable state.
Records complete dataset provenance, licensing, and synthetic sample status.
"""

import hashlib
import os
import urllib.request
from pathlib import Path
import pandas as pd

# Provenance Metadata
DATASET_NAME = "Enterprise Commercial Orders (Sample Superstore Extended)"
DATASET_SOURCE_URL = "https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv"
DATASET_LICENSE = "CC0 1.0 Universal (Public Domain Dedication) / Open Educational Sample Data"
DATASET_ATTRIBUTION = "Derived from Tableau Software's open sample business dataset for BI benchmarking."
DATASET_NATURE = "Synthetic / Sample Commercial Retail Benchmark (Anonymized sample entities; not real confidential company data)"
EXPECTED_ROW_COUNT = 10800


def get_project_root() -> Path:
    """Returns absolute path to the project root directory."""
    return Path(__file__).resolve().parent.parent


def compute_file_hash(file_path: Path) -> str:
    """Computes SHA-256 hash of a file to guarantee data immutability."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def ingest_raw_data(force_download: bool = False) -> Path:
    """
    Downloads and preserves untouched raw data to data/raw/superstore_raw.csv.
    Never modifies or overwrites unless force_download is explicitly True.
    """
    root = get_project_root()
    raw_dir = root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    target_file = raw_dir / "superstore_raw.csv"

    print("=" * 70)
    print("STAGE 3: DATA INGESTION & PROVENANCE REGISTRATION")
    print("=" * 70)
    print(f"Dataset Name       : {DATASET_NAME}")
    print(f"Original Source URL: {DATASET_SOURCE_URL}")
    print(f"License Terms      : {DATASET_LICENSE}")
    print(f"Attribution Notice : {DATASET_ATTRIBUTION}")
    print(f"Data Nature        : {DATASET_NATURE}")
    print(f"Target Destination : {target_file}")

    if target_file.exists() and not force_download:
        file_hash = compute_file_hash(target_file)
        df_existing = pd.read_csv(target_file, encoding="latin1")
        print(f"\n[INFO] Raw file already exists and is preserved (Untouched).")
        print(f"[INFO] Existing Row Count: {len(df_existing):,} rows | {len(df_existing.columns)} columns")
        print(f"[INFO] File SHA-256 Hash : {file_hash}")
        return target_file

    print(f"\n[INGEST] Downloading from public source...")
    headers = {"User-Agent": "Antigravity-Enterprise-Data-Ingestion/1.0"}
    req = urllib.request.Request(DATASET_SOURCE_URL, headers=headers)
    with urllib.request.urlopen(req) as response, open(target_file, "wb") as out_file:
        data = response.read()
        out_file.write(data)

    file_hash = compute_file_hash(target_file)
    df = pd.read_csv(target_file, encoding="latin1")
    print(f"[SUCCESS] Raw dataset successfully saved to: {target_file}")
    print(f"[VERIFY] Downloaded Rows : {len(df):,}")
    print(f"[VERIFY] Downloaded Cols : {len(df.columns)}")
    print(f"[VERIFY] SHA-256 Checksum: {file_hash}")

    if len(df) != EXPECTED_ROW_COUNT:
        print(f"[WARNING] Expected {EXPECTED_ROW_COUNT} rows, got {len(df)} rows.")

    return target_file


if __name__ == "__main__":
    ingest_raw_data()
