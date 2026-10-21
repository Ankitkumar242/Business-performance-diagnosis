# SQL QUERY & ANALYTICAL VIEW CATALOG
## Business Performance Diagnosis & Decision Intelligence Platform

**Database Engine:** SQLite 3 (`sql/business_bi.db`)  
**Schema Model:** Kimball Star Schema (1 FactOrders, 1 FactTargets, 5 Dimensions)  
**Foreign Key Enforcement:** `PRAGMA foreign_keys = ON;`  
**Catalog Status:** Production Ready & Verified  

---

## 1. PRODUCTION BI ANALYTICAL VIEWS

### VIEW 1: `v_monthly_financials`
- **Business Question:** What is the monthly trajectory of gross revenue, COGS, profit, gross margin %, and average order value across the 4-year horizon?
- **Grain:** One row per calendar month (`YearMonth` from `2015-01` to `2018-12`, 48 rows).
- **Core Formulae:**
  - $\text{TotalRevenue} = \sum \text{Sales}$
  - $\text{TotalCOGS} = \sum \text{COGS}$
  - $\text{TotalProfit} = \sum \text{Profit}$
  - $\text{GrossMarginPct} = \frac{\sum \text{Profit}}{\text{NULLIF}(\sum \text{Sales}, 0)}$
  - $\text{AvgOrderValue} = \frac{\sum \text{Sales}}{\text{NULLIF}(\text{COUNT(DISTINCT OrderID)}, 0)}$
- **Underlying Tables:** `fact_orders` $\bowtie$ `dim_date` on `OrderDateKey = DateKey`.
- **Validation Method:** Sum of `TotalRevenue` across all 48 rows must equal \$2,297,200.86 with \$0.00 discrepancy.

---

### VIEW 2: `v_target_variance_decomposition`
- **Business Question:** Is the business achieving its monthly budgeted targets across regions and product categories, and where are the largest dollar variances?
- **Grain:** One row per `YearMonth` $\times$ `Region` $\times$ `Category` (576 rows).
- **Core Formulae:**
  - $\text{RevenueVarianceDollar} = \text{ActualRevenue} - \text{TargetRevenue}$
  - $\text{RevenueAchievementPct} = \frac{\text{ActualRevenue} \times 100}{\text{NULLIF}(\text{TargetRevenue}, 0)}$
  - $\text{ProfitVarianceDollar} = \text{ActualProfit} - \text{TargetProfit}$
  - $\text{ProfitAchievementPct} = \frac{\text{ActualProfit} \times 100}{\text{NULLIF}(\text{TargetProfit}, 0)}$
  - $\text{MarginVariancePct} = \text{ActualMarginPct} - \text{TargetMarginPct}$
- **Underlying Tables:** `fact_targets` $\overset{\text{LEFT}}{\bowtie}$ `(fact_orders` $\bowtie$ `dim_date` $\bowtie$ `dim_geography` $\bowtie$ `dim_product)`.
- **Validation Method:** Row count equals 576; sum of `ActualRevenue` matches portfolio revenue (\$2,297,200.86).

---

### VIEW 3: `v_regional_performance`
- **Business Question:** Which geographical regions are driving healthy profit margins vs. exhibiting severe margin drag and customer returns?
- **Grain:** One row per `Region` (4 rows: Central, East, South, West).
- **Core Formulae:**
  - $\text{GrossMarginPct} = \frac{\sum \text{Profit}}{\sum \text{Sales}}$
  - $\text{LossMakingSharePct} = \frac{\sum \text{IsLossMaking} \times 100}{\text{COUNT(*)}}$
  - $\text{CashLeakageDollar} = \sum |\text{Profit}| \quad (\text{WHERE Profit } < 0)$
  - $\text{ReturnRatePct} = \frac{\sum \text{IsReturned} \times 100}{\text{COUNT(*)}}$
- **Underlying Tables:** `fact_orders` $\bowtie$ `dim_geography` on `GeographyID`.
- **Validation Method:** Group-by sum of revenue across the 4 regions matches \$2,297,200.86.

---

### VIEW 4: `v_subcategory_profitability`
- **Business Question:** Which product lines are profitable stars, and which are chronic loss-makers requiring pricing floors or catalog rationalization?
- **Grain:** One row per `Category` $\times$ `SubCategory` (17 rows).
- **Core Formulae:**
  - $\text{ProfitabilityTier} = \begin{cases} \text{'Loss-Making Sub-Category'} & \text{if Profit } < 0 \\ \text{'Low Margin (<10\%)'} & \text{if Margin } < 0.10 \\ \text{'Healthy Margin (>=10\%)'} & \text{otherwise} \end{cases}$
  - $\text{NegativeProfitTally} = \sum \text{Profit} \quad (\text{WHERE Profit } < 0)$
- **Underlying Tables:** `fact_orders` $\bowtie$ `dim_product` on `ProductID`.
- **Validation Method:** 17 distinct sub-categories accounted for; loss-making sub-categories (*Tables*, *Bookcases*, *Supplies*) flagged.

---

### VIEW 5: `v_discount_bracket_margin_leakage`
- **Business Question:** At what specific discount depth does commercial profitability collapse into negative cash flow?
- **Grain:** One row per `DiscountBracket` (5 rows: 0%, 1–10%, 11–20%, 21–40%, >40%).
- **Core Formulae:**
  - $\text{LossMakingRatePct} = \frac{\sum \text{IsLossMaking} \times 100}{\text{COUNT(*)}}$
  - $\text{CashLeakageDollar} = \sum |\text{Profit}| \quad (\text{WHERE Profit } < 0)$
- **Underlying Tables:** `fact_orders`.
- **Validation Method:** Total transactions across 5 brackets equal 9,994; confirms that brackets $>20\%$ experience negative gross margins.

---

## 2. ADVANCED BUSINESS QUERIES CATALOG

| Query Name | Business Focus | Advanced SQL Constructs | Expected Row Output |
| :--- | :--- | :--- | :---: |
| **Query 1: MoM Financial Velocity** | Sequential monthly growth trends & momentum | CTEs, `LAG() OVER(ORDER BY YearMonth)`, zero division protection | 48 rows |
| **Query 2: Pareto Sub-Category Contribution** | 80/20 Rule revenue & profit drivers | `RANK()`, `SUM() OVER(ORDER BY Sales DESC)` cumulative running totals | 17 rows |
| **Query 3: Regional Margin Erosion Ranking** | Worst-to-best profitability ranking | `DENSE_RANK() OVER(ORDER BY Margin ASC)`, cash leakage aggregation | 4 rows |
| **Query 4: Top 3 Loss Leaders per Region** | SKU-level loss concentration by territory | CTEs, `ROW_NUMBER() OVER(PARTITION BY Region ORDER BY Profit ASC)` | 12 rows (4 reg $\times$ 3 SKUs) |
| **Query 5: Annual Target Achievement** | Multi-year budget commitment tracking | Multiple CTE aggregation, cross-year target vs actual join | 4 rows (2015 to 2018) |
| **Query 6: Carrier Shipping SLA Adherence** | Logistics fulfillment cycle times & SLA rates | `CASE` expression on `FulfillmentDays <= StandardSLADays`, `AVG`, `MIN`, `MAX` | 4 rows (Ship modes) |
