# DATA QUALITY & PROFILING AUDIT REPORT
## Business Performance Diagnosis & Decision Intelligence Platform

**Audit Execution Date:** October 14, 2026  
**Pipeline Stage:** Stage 3 (Ingestion, Profiling, Cleaning & Validation)  
**Status:** ALL QUALITY ASSERTIONS PASSED (6/6)  

---

## 1. DATASET PROVENANCE & RECORD ACCOUNTABILITY

| Metric | Raw Ingestion Stage | Post-Cleaning Stage | Variance / Disposition |
| :--- | :--- | :--- | :--- |
| **Total Ingested Records** | **10,800** | **10,800** | $0$ records lost (100% accounted for) |
| **Transactional Order Lines** | 10,800 (mixed) | **9,994** | Retained as operational order line items |
| **Regional Managers (People)** | Embedded in CSV | **4** | Extracted to `dim_regional_managers.csv` |
| **Order Returns** | Embedded in CSV | **800** (296 unique) | Extracted to `order_returns.csv` |
| **Structural Delimiter Headers** | Embedded in CSV | **2** | Documented and excluded from transactions |

---

## 2. PRE-CLEANING VS. POST-CLEANING COMPARISON

| Data Quality Attribute | Pre-Cleaning Value | Post-Cleaning Value | Treatment & Business Rationale |
| :--- | :--- | :--- | :--- |
| **Postal Code Missingness** | 817 missing | **0 missing (0.0%)** | 11 Burlington, Vermont records imputed with valid zip `05408`; 806 empty rows segregated. |
| **Missing Transaction Data** | 806 rows with nulls | **0 nulls (0.0%)** | Unbundled non-transactional sheets (People, Returns). |
| **Date Inversions** | 0 inversions | **0 inversions** | Verified that $\text{Ship Date} \ge \text{Order Date}$ for 100% of records. |
| **Lead Time Range** | 0 to 7 days | **0 to 7 days** | Average fulfillment cycle time: 3.96 days. |
| **Total Sales Volume** | \$2,297,200.86 | **\$2,297,200.86** | Exact match: \$0.00 discrepancy ($0.00$). |
| **Total Net Profit** | \$286,397.02 | **\$286,397.02** | Exact match: \$0.00 discrepancy ($0.00$). |
| **Primary Key Uniqueness** | 504 raw duplicate rows | **9,994 unique Row IDs** | Row ID is strictly unique (100% primary key integrity). |

---

## 3. BUSINESS DIAGNOSTIC FLAGS CREATED

- **Loss-Making Orders:** **1,871 transactions** (18.72%) operated at negative profit, generating a cumulative cash leakage of **\$156,131.29**.
- **Returned Order Lines:** **800 order lines** (8.0%) are confirmed as returned by customers.
- **Discount Brackets Formulated:** Categorized into 5 distinct tiers (0%, 1-10%, 11-20%, 21-40%, >40%) for pricing elasticity and margin erosion analysis.

---

## 4. FORMAL AUDIT SIGN-OFF
The clean transaction dataset (`data/processed/clean_transactions.csv`) satisfies all enterprise database and BI modeling prerequisites. Ready for Stage 4 Star Schema dimensionalization.
