# DATASET PROVENANCE, LICENSING & GOVERNANCE DOCUMENT
## Business Performance Diagnosis & Decision Intelligence Platform

**Document Version:** 1.0  
**Effective Date:** October 14, 2026  
**Governance Status:** Formally Audited Prior to Stage 3 Implementation  

---

## 1. PRIMARY TRANSACTIONAL DATASET

### 1.1 Source & Lineage
- **Dataset Title:** Commercial Retail & Enterprise Distribution Orders (Superstore Extended Dataset)
- **Primary Source Repository:** Tableau Community Sample Data / Public Mirror
- **Direct Acquisition URL:** `https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv`
- **Format:** Comma-Separated Values (`.csv`), Latin-1 / UTF-8 compatible
- **Observed Record Count:** **10,800 rows** across 21 columns
- **Temporal Horizon:** **January 3, 2015 to December 30, 2018** (4 full calendar years)

### 1.2 Nature of the 10,800 Rows: Real vs. Synthetic Clarification
> **GOVERNANCE STATEMENT ON DATA REALISM:**  
> The 10,800 transactional records represent **realistic commercial sample retail data originally created by Tableau Software for enterprise training, benchmarking, and dashboard demonstration**. 
> - **Customer Names:** Synthetic / anonymized customer names (e.g., "Claire Gute", "Darrin Van Huff") to prevent any Personally Identifiable Information (PII) leakage, fully compliant with GDPR and India's Digital Personal Data Protection (DPDP) Act.
> - **Product Catalog & Geography:** Realistic North American corporate office products, technology hardware, furniture, US states, and cities.
> - **Financial Values:** Realistic corporate transaction amounts (`Sales`, `Quantity`, `Discount`, `Profit`) modeled on commercial retail distribution patterns.
> - **Attribution:** This data is **NOT** proprietary internal data of Genpact, Infosys, or any multinational employer. It is an open benchmark dataset.

### 1.3 Legal Reuse License
- **License Classification:** **CC0 1.0 Universal (Public Domain Dedication) / Open Educational Sample Data**
- **Commercial & Portfolio Terms:** Free to use, adapt, modify, analyze, and distribute for non-commercial and portfolio display purposes without copyright infringement or licensing fees.
- **Data Preservation Rule:** The raw ingested CSV file (`data/raw/superstore_raw.csv`) is treated as **read-only and immutable**. All transformations, cleansing, and profiling will write exclusively to `data/processed/` and `data/profiling/`.

---

## 2. SECONDARY TARGET DATASET (`FactTargets`)

### 2.1 Explicit Labeling: 100% Synthetic Managerial Targets
> [!IMPORTANT]
> **SYNTHETIC DATA DECLARATION:**  
> The monthly targets in `FactTargets` are **100% SYNTHETIC MANAGERIAL BENCHMARKS**, generated mathematically for variance analysis. They are **NOT** confidential, proprietary, or actual internal targets of any corporate entity.

### 2.2 Calibration Methodology
Because real enterprise performance diagnosis requires evaluating actual results against budgeted targets (quotas), and public transactional datasets do not contain internal corporate financial budgets, a realistic target table is generated via `src/generate_targets.py`:
- **Grain:** Monthly target by `Year`, `Month`, `Region`, and `Category` (48 months $\times$ 4 regions $\times$ 3 categories $= \mathbf{576\text{ rows}}$).
- **Target Revenue Formula:** Historical baseline monthly sales $\times$ seasonal factor $\times$ annual growth expectation (8.0%–12.0%) $\times$ managerial variance factor ($\pm 10\%$).
- **Target Profit Formula:** $\text{Target Revenue} \times 15.0\%$ target gross margin benchmark.
- **Reproducibility:** Seeded with `random_state = 42` to guarantee exact deterministic reproducibility across all environments.

---

## 3. AUDIT SIGN-OFF BEFORE STAGE 3
This documentation satisfies Condition #2 of the project governance charter:
1. Source URL is verified and accessible.
2. License terms are recorded (CC0 / Open Sample).
3. The real vs. synthetic nature of the 10,800 transactional records is transparently disclosed.
4. The synthetic nature of `FactTargets` is unambiguously declared.
