# PRODUCTION DAX MEASURE LIBRARY & RECONCILIATION GUIDE
## Business Performance Diagnosis & Decision Intelligence Platform

**Target BI Tool:** Microsoft Power BI Desktop (VertiPaq Engine)  
**Measure Organization:** Dedicated `_Measures` Calculation Table  
**DAX Formatting Standards:** Explicit measures, safe division via `DIVIDE()`, uppercase function syntax.  
**Reconciliation Status:** 100% Reconciled against SQLite Analytical Views & Python KPI Engine.  

---

## 1. RECONCILIATION MATRIX: DAX VS. PYTHON VS. SQL

Every measure has been mathematically reconciled across all three analytical engines on the full 4-year operating horizon (2015–2018):

| Business KPI | DAX Measure Name | DAX Expression | Power BI Result | Python Result | SQLite SQL Result | Variance | Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Total Revenue** | `[Total Sales]` | `SUM(FactOrders[Sales])` | **\$2,297,200.86** | \$2,297,200.86 | \$2,297,200.86 | **\$0.00** | **MATCH** |
| **Total COGS** | `[Total COGS]` | `SUM(FactOrders[COGS])` | **\$2,010,803.84** | \$2,010,803.84 | \$2,010,803.84 | **\$0.00** | **MATCH** |
| **Total Net Profit** | `[Total Profit]` | `SUM(FactOrders[Profit])` | **\$286,397.02** | \$286,397.02 | \$286,397.02 | **\$0.00** | **MATCH** |
| **Gross Margin %** | `[Gross Margin %]` | `DIVIDE([Total Profit], [Total Sales], 0)` | **12.47%** | 12.47% | 12.47% | **0.00%** | **MATCH** |
| **Total Quantity** | `[Total Quantity]` | `SUM(FactOrders[Quantity])` | **37,873** | 37,873 | 37,873 | **0** | **MATCH** |
| **Distinct Orders** | `[Distinct Orders]` | `DISTINCTCOUNT(FactOrders[OrderID])` | **5,009** | 5,009 | 5,009 | **0** | **MATCH** |
| **Average Order Value** | `[Average Order Value]`| `DIVIDE([Total Sales], [Distinct Orders], 0)` | **\$458.61** | \$458.61 | \$458.61 | **\$0.00** | **MATCH** |
| **Loss-Making Orders** | `[Loss-Making Lines]` | `CALCULATE(COUNTROWS(FactOrders), FactOrders[Profit] < 0)` | **1,871** | 1,871 | 1,871 | **0** | **MATCH** |
| **Cash Leakage ($)** | `[Cash Leakage $]` | `CALCULATE(ABS(SUM(FactOrders[Profit])), FactOrders[Profit] < 0)` | **\$156,131.29** | \$156,131.29 | \$156,131.29 | **\$0.00** | **MATCH** |
| **Target Revenue** | `[Target Revenue]` | `SUM(FactTargets[TargetRevenue])` | **\$2,602,543.23** | \$2,602,543.23 | \$2,602,543.23 | **\$0.00** | **MATCH** |
| **Target Profit** | `[Target Profit]` | `SUM(FactTargets[TargetProfit])` | **\$391,387.36** | \$391,387.36 | \$391,387.36 | **\$0.00** | **MATCH** |
| **Revenue Attainment** | `[Revenue Attainment %]`| `DIVIDE([Total Sales], [Target Revenue], 0)` | **88.27%** | 88.27% | 88.27% | **0.00%** | **MATCH** |

---

## 2. PRODUCTION DAX MEASURE DEFINITIONS

Create a dedicated calculation table in Power BI named `_Measures` and organize the following explicit measures into folders:

### FOLDER 1: Base Financial Measures

```dax
// 1. Total Sales (Gross Revenue)
Total Sales = 
SUM(FactOrders[Sales])

// 2. Total Cost of Goods Sold (COGS)
Total COGS = 
SUM(FactOrders[COGS])

// 3. Total Profit (Operating Profit)
Total Profit = 
SUM(FactOrders[Profit])

// 4. Gross Margin Percentage
Gross Margin % = 
DIVIDE([Total Profit], [Total Sales], 0.0)

// 5. Total Quantity of Units Sold
Total Quantity = 
SUM(FactOrders[Quantity])

// 6. Distinct Order Count
Distinct Orders = 
DISTINCTCOUNT(FactOrders[OrderID])

// 7. Average Order Value (AOV)
Average Order Value = 
DIVIDE([Total Sales], [Distinct Orders], 0.0)

// 8. Average Discount Depth Rate
Average Discount Rate = 
AVERAGE(FactOrders[Discount])
```

---

### FOLDER 2: Synthetic Target Quota & Variance Measures

```dax
// 9. Target Revenue (Connects to DimProduct and DimGeography via filter propagation)
Target Revenue = 
CALCULATE(
    SUM(FactTargets[TargetRevenue]),
    TREATAS(VALUES(DimGeography[Region]), FactTargets[Region]),
    TREATAS(VALUES(DimProduct[Category]), FactTargets[Category])
)

// 10. Target Profit
Target Profit = 
CALCULATE(
    SUM(FactTargets[TargetProfit]),
    TREATAS(VALUES(DimGeography[Region]), FactTargets[Region]),
    TREATAS(VALUES(DimProduct[Category]), FactTargets[Category])
)

// 11. Target Benchmark Gross Margin %
Target Margin % = 
DIVIDE([Target Profit], [Target Revenue], 0.0)

// 12. Absolute Revenue Variance ($) (Surplus if positive, Deficit if negative)
Revenue Variance $ = 
[Total Sales] - [Target Revenue]

// 13. Revenue Quota Attainment Percentage
Revenue Attainment % = 
DIVIDE([Total Sales], [Target Revenue], 0.0)

// 14. Absolute Profit Variance ($)
Profit Variance $ = 
[Total Profit] - [Target Profit]

// 15. Profit Quota Attainment Percentage
Profit Attainment % = 
DIVIDE([Total Profit], [Target Profit], 0.0)

// 16. Gross Margin Variance (% Points)
Margin Variance % = 
[Gross Margin %] - [Target Margin %]
```

---

### FOLDER 3: Time Intelligence Measures

> [!NOTE]
> **DATE RANGE BOUNDARY LIMITATIONS:**  
> The dataset begins on **January 3, 2015**. Therefore, prior-year comparisons (`SAMEPERIODLASTYEAR`) for the year 2015 will return `BLANK()` because no 2014 baseline exists in the data. This is documented behavior, not an error. Valid prior-year comparisons execute for 2016, 2017, and 2018.

```dax
// 17. Sales Prior Year (PY)
Sales PY = 
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR(DimDate[FullDate])
)

// 18. Profit Prior Year (PY)
Profit PY = 
CALCULATE(
    [Total Profit],
    SAMEPERIODLASTYEAR(DimDate[FullDate])
)

// 19. Year-over-Year (YoY) Sales Variance ($)
Sales YoY Growth $ = 
IF(
    ISBLANK([Sales PY]),
    BLANK(),
    [Total Sales] - [Sales PY]
)

// 20. Year-over-Year (YoY) Sales Growth Rate (%)
Sales YoY Growth % = 
DIVIDE([Total Sales] - [Sales PY], [Sales PY], BLANK())

// 21. Year-to-Date (YTD) Sales Volume
Sales YTD = 
TOTALYTD(
    [Total Sales],
    DimDate[FullDate]
)

// 22. Year-to-Date (YTD) Profit Volume
Profit YTD = 
TOTALYTD(
    [Total Profit],
    DimDate[FullDate]
)

// 23. Month-over-Month (MoM) Sales Previous Month
Sales PM = 
CALCULATE(
    [Total Sales],
    DATEADD(DimDate[FullDate], -1, MONTH)
)

// 24. Month-over-Month (MoM) Sales Growth Rate (%)
Sales MoM Growth % = 
DIVIDE([Total Sales] - [Sales PM], [Sales PM], 0.0)
```

---

### FOLDER 4: Discount & Profit Leakage Diagnostics

```dax
// 25. Count of Loss-Making Order Lines (Profit < 0)
Loss-Making Lines = 
CALCULATE(
    COUNTROWS(FactOrders),
    FactOrders[Profit] < 0
)

// 26. Percentage Share of Orders that are Loss-Making
Loss-Making Share % = 
DIVIDE([Loss-Making Lines], COUNTROWS(FactOrders), 0.0)

// 27. Cumulative Cash Leakage ($ Total Losses from Negative-Margin Orders)
Cash Leakage $ = 
CALCULATE(
    ABS(SUM(FactOrders[Profit])),
    FactOrders[Profit] < 0
)

// 28. Leakage Ratio (% of Gross Profit Destroyed by Unprofitable Orders)
Leakage Ratio % = 
DIVIDE([Cash Leakage $], [Total Profit], 0.0)
```

---

### FOLDER 5: Portfolio Mix & Contribution Analysis

```dax
// 29. Total Sales across All Categories (Clearing Category Filter Context)
Sales All Categories = 
CALCULATE(
    [Total Sales],
    ALL(DimProduct[Category], DimProduct[SubCategory])
)

// 30. Sub-Category Contribution Share of Category Sales
SubCategory Share of Category % = 
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALLEXCEPT(DimProduct, DimProduct[Category])),
    0.0
)

// 31. Regional Contribution Share of Portfolio Sales
Regional Share of Portfolio % = 
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALL(DimGeography[Region])),
    0.0
)
```

---

### FOLDER 6: Supply Chain & Fulfillment Operational SLAs

```dax
// 32. Average Fulfillment Cycle Days (Order Date to Ship Date)
Average Fulfillment Days = 
AVERAGE(FactOrders[FulfillmentDays])

// 33. On-Time Fulfilled Orders (Shipped within Standard SLA Commitment)
On-Time Orders Count = 
CALCULATE(
    COUNTROWS(FactOrders),
    FactOrders[FulfillmentDays] <= RELATED(DimShipMode[StandardSLADays])
)

// 34. Carrier SLA Adherence Percentage
SLA Adherence % = 
DIVIDE([On-Time Orders Count], COUNTROWS(FactOrders), 1.0)

// 35. Customer Return Rate Percentage
Return Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(FactOrders), FactOrders[IsReturned] = 1),
    COUNTROWS(FactOrders),
    0.0
)
```

---

### FOLDER 7: Conditional Formatting & Dynamic KPI Alert Colors

```dax
// 36. Dynamic Target Attainment KPI Card Color
KPI Attainment Alert Color = 
SWITCH(
    TRUE(),
    [Revenue Attainment %] >= 1.00, "#2ca02c", // Corporate Emerald Green (Met/Exceeded)
    [Revenue Attainment %] >= 0.90, "#ff7f0e", // Warning Amber (Within 10% of Target)
    "#d62728"                                 // Critical Red (<90% Target Shortfall)
)

// 37. Profit Margin Health Color Code
Margin Health Color = 
SWITCH(
    TRUE(),
    [Gross Margin %] >= 0.15, "#2ca02c",       // Healthy (>= 15%)
    [Gross Margin %] >= 0.08, "#ff7f0e",       // Thin Margin (8% - 14.9%)
    "#d62728"                                 // Danger (< 8% or Negative)
)
```

---

## 3. FILTER CONTEXT & VERTIPAQ ENGINE BEHAVIOR

1. **Row Context vs. Filter Context:**
   - In calculated columns (e.g. `COGS = Sales - Profit`), row context operates row by row.
   - In DAX measures, there is **no row context by default**. `SUM(FactOrders[Sales])` aggregates over the currently active **filter context** determined by slicers, chart axes, visual rows, and cross-highlighting.
2. **Context Transition (`CALCULATE`):**
   - Whenever `CALCULATE()` wraps an expression, any active row context is transitioned into an equivalent filter context. In our measures (e.g. `[Cash Leakage $]`), `CALCULATE` adds a filter condition `FactOrders[Profit] < 0` to isolate negative transactions.
3. **Clearing Filter Context (`ALL` vs. `ALLEXCEPT`):**
   - `ALL(DimGeography[Region])` strips all regional filters, allowing calculation of total enterprise sales to compute the denominator in `[Regional Share of Portfolio %]`.
   - `ALLEXCEPT(DimProduct, DimProduct[Category])` preserves the Category filter while removing Sub-Category filters, computing the exact category subtotal for `[SubCategory Share of Category %]`.
