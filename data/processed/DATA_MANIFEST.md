# PROCESSED DATA PACK MANIFEST & SCHEMA AUDIT
## Business Performance Diagnosis & Decision Intelligence Platform

**Export Directory:** `data/processed/`  
**Target Ingestion Platform:** Microsoft Power BI Desktop & SQLite Analytical Warehouse  
**Audit Date:** October 14, 2026  
**Preservation Rule:** The raw source file `data/raw/superstore_raw.csv` remains strictly untouched, immutable, and preserved.  

---

## 1. FILE MANIFEST & SPECIFICATIONS

| # | File Name | Row Count | Column Count | File Size (Bytes) | Table Grain | Primary Key | Intended Usage in Power BI / SQL |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| **1** | **`fact_orders.csv`** | **9,994** | 19 | ~1,320,472 | One row per order line item | `RowID` | Core transactional fact table for sales, profit, discounts, and order-level KPIs. |
| **2** | **`fact_targets.csv`** | **576** | 11 | ~60,134 | One row per YearMonth $\times$ Region $\times$ Category | `TargetID` | Budget quota fact table for target attainment and arithmetic variance modeling *(Synthetic)*. |
| **3** | **`dim_date.csv`** | **1,826** | 14 | ~137,534 | One row per calendar day (2015-01-01 to 2019-12-31) | `DateKey` | Conformed calendar dimension marked as official Date Table in Power BI for Time Intelligence. |
| **4** | **`dim_customer.csv`** | **793** | 3 | ~26,859 | One row per unique customer account | `CustomerID` | Customer dimension for account-level and commercial segment analysis (Consumer, Corporate, Home Office). |
| **5** | **`dim_product.csv`** | **1,862** | 4 | ~144,612 | One row per unique product SKU | `ProductID` | Product catalog hierarchy dimension (Category $\rightarrow$ Sub-Category $\rightarrow$ SKU). |
| **6** | **`dim_geography.csv`** | **632** | 6 | ~31,641 | One row per unique City/State/PostalCode combination | `GeographyID` | Geographic hierarchy dimension (Country $\rightarrow$ Region $\rightarrow$ State $\rightarrow$ City). |
| **7** | **`dim_ship_mode.csv`** | **4** | 3 | ~106 | One row per shipping class | `ShipModeID` | Logistics dimension containing carrier SLA benchmarks (0, 2, 4, 6 days). |
| **8** | **`clean_transactions.csv`** | **9,994** | 27 | ~3,042,651 | One row per order line item (Denormalized) | `Row ID` | Cleaned master denormalized flat file used for Python exploratory data analysis. |
| **9** | **`dim_regional_managers.csv`** | **4** | 2 | ~111 | One row per corporate region | `Region` | Regional General Manager reference lookup extracted from original bundled sheets. |
| **10** | **`order_returns.csv`** | **800** | 2 | ~16,024 | One row per customer return log (296 unique orders) | `OrderID` | Returns audit table extracted from original bundled sheets for return rate calculation. |

---

## 2. RECONCILIATION TOTALS OF THE PROCESSED PACK

- **Total Ingested Records in Raw File:** Exactly 10,800 records.
- **Accounted Records in Processed Pack:**
  - $9,994\text{ (Orders)} + 4\text{ (Regional Managers)} + 800\text{ (Returns)} + 2\text{ (Delimiters)} = \mathbf{10,800\text{ (100\% match, 0 lost)}}$.
- **Cumulative Financial Totals:**
  - `FactOrders` Total Revenue: **\$2,297,200.86**
  - `FactOrders` Total Profit: **\$286,397.02**
  - `FactTargets` Total Quota Revenue: **\$2,602,543.23** *(Synthetic)*
  - `FactTargets` Total Quota Profit: **\$391,387.36** *(Synthetic)*
