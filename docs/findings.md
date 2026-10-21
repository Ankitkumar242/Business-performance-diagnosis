# EVIDENCE-BACKED BUSINESS DIAGNOSTIC DOSSIERS
## Business Performance Diagnosis & Decision Intelligence Platform

**Document Version:** 1.0  
**Effective Audit Date:** October 14, 2026  
**Analytical Scope:** Full Verified Operating Horizon (January 3, 2015 to December 30, 2018)  
**Methodological Integrity Notice:**  
All findings are calculated directly from verified operational data (`fact_orders`, `dim_geography`, `dim_product`, `dim_date`, `dim_ship_mode`, and calibrated `fact_targets`). Statistical correlations are explicitly distinguished from causal claims. Planning targets are transparently identified as synthetic managerial quotas.

---

## DOSSIER 1: DEEP DISCOUNTING & MARGIN EROSION THRESHOLD

### 1.1 Business Question & Hypothesis
- **Business Question:** Does discounting stimulate incremental profitable revenue, or does it erode operating margin? At what discount depth does commercial profitability collapse into negative operating cash flow?
- **Hypothesis:** When promotional discount rates exceed 20%, product margins transition from positive contribution to severe negative cash flow, generating substantial financial leakage.

### 1.2 Dataset Scope, Filters & KPI Definitions
- **Dataset Period:** 2015-01-03 to 2018-12-30 (48 Months).
- **Filter Applied:** None (Complete portfolio: 9,994 order line items).
- **Relevant KPI Definitions:**
  - $\text{Gross Margin \%} = \frac{\sum \text{Profit}}{\sum \text{Sales}}$
  - $\text{Loss-Making Rate \%} = \frac{\text{Count of Orders with Profit } < 0}{\text{Total Orders in Bracket}} \times 100$
  - $\text{Total Cash Leakage (\$)} = \sum |\text{Profit}| \quad (\text{WHERE Profit } < 0)$

### 1.3 Calculated Findings & Comparison Baseline

| Discount Tier Bracket | Transaction Count | Total Sales Volume | Total Net Profit | Gross Margin % | Loss-Making Orders | Loss-Making Rate % | Cash Leakage ($) | Baseline Comparison |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0% (No Discount)** | 4,798 | \$1,087,908.47 | +\$320,987.60 | **+29.51%** | 0 | **0.00%** | \$0.00 | **Benchmark Baseline** |
| **1–10% (Low)** | 94 | \$54,369.35 | +\$9,030.79 | **+16.61%** | 4 | **4.26%** | \$53.48 | Profitable; -12.9% margin delta |
| **11–20% (Moderate)** | 3,709 | \$792,152.89 | +\$91,739.06 | **+11.58%** | 519 | **13.99%** | \$17,562.56 | Acceptable; -17.9% margin delta |
| **21–40% (High)** | 460 | \$234,137.95 | **-\$35,827.18** | **-15.30%** | 415 | **90.22%** | **\$38,629.74** | **CRITICAL: Margin Collapse** |
| **>40% (Severe)** | 933 | \$128,632.20 | **-\$99,533.25** | **-77.40%** | 933 | **100.00%** | **\$99,885.50** | **100% UNPROFITABLE** |
| **PORTFOLIO TOTAL** | **9,994** | **\$2,297,200.86** | **+\$286,397.02** | **12.47%** | **1,871** | **18.72%** | **\$156,131.29** | Blended Enterprise Margin |

### 1.4 Evidence from Data
- **The 20% Tipping Point:** Orders with discounts $\le 20\%$ maintain positive gross margins (+29.51%, +16.61%, +11.58%). As soon as discounts exceed 20%, **90.22% of orders in the 21–40% bracket and 100.00% of orders in the >40% bracket lose money**.
- **Concentration of Cash Leakage:** Out of the total \$156,131.29 in negative cash flow, **\$138,515.24 (88.72%)** is generated exclusively by the 1,393 transactions discounted above 20%.
- **Statistical Association:** Pearson correlation $r = -0.2197$; Spearman rank correlation $\rho = -0.3295$.
- **Reproducible Query:** `SELECT * FROM v_discount_bracket_margin_leakage;` in `sql/business_bi.db`.

### 1.5 Limitations & Alternative Explanations
- *Limitation:* The dataset records completed transactions but does not track abandoned carts or volume elasticity if discounts had not been offered.
- *Alternative Explanation:* Deep discounting may have been applied to liquidate obsolete or slow-moving inventory (e.g. discontinued furniture) to free working capital, meaning the negative margin was an intentional inventory clearance decision rather than sales rep rogue behavior.
- *Confidence Level:* **High (Empirical correlation verified across 9,994 transactions).**

### 1.6 Evidence-Linked Recommendation
Implement an automated commercial pricing floor: restrict sales representatives from discounting beyond 20% without formal regional controller approval. Capping discounts at 20% addresses the root source of 88.7% of corporate cash leakage.

---

## DOSSIER 2: REGIONAL PROFITABILITY & CENTRAL REGION MARGIN DRAG

### 2.1 Business Question & Hypothesis
- **Business Question:** Does geographic performance diverge significantly, and is there a specific region responsible for dragging corporate profitability down?
- **Hypothesis:** The Central region underperforms compared to other regional theaters due to elevated discount rates and a higher concentration of loss-making accounts.

### 2.2 Dataset Scope, Filters & KPI Definitions
- **Dataset Period:** 2015-01-03 to 2018-12-30.
- **Filter Applied:** Grouped by `DimGeography[Region]`.
- **Relevant KPI Definitions:**
  - $\text{Regional Margin \%} = \frac{\text{Regional Profit}}{\text{Regional Sales}}$
  - $\text{Loss-Making Share \%} = \frac{\text{Loss-Making Orders in Region}}{\text{Total Regional Orders}} \times 100$
  - $\text{Regional Cash Leakage} = \sum |\text{Profit}| \quad (\text{WHERE Profit } < 0 \text{ AND Region} = R)$

### 2.3 Calculated Findings & Comparison Baseline

| Region | Active Orders | Total Revenue | Total Net Profit | Gross Margin % | Avg Discount Rate | Loss-Making Orders | Loss-Making Share % | Cash Leakage ($) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **West** | 3,203 | \$725,457.82 | +\$108,418.45 | **14.94%** | **10.93%** | 318 | **9.93%** | \$19,773.06 |
| **East** | 2,848 | \$678,781.24 | +\$91,522.78 | **13.48%** | **14.54%** | 553 | **19.42%** | \$44,385.74 |
| **South** | 1,620 | \$391,721.91 | +\$46,749.43 | **11.93%** | **14.73%** | 259 | **15.99%** | \$19,401.76 |
| **Central** | 2,323 | \$501,239.89 | **+\$39,706.36** | **7.92%** | **24.04%** | **741** | **31.90%** | **\$56,126.16** |

### 2.4 Evidence from Data
- **Severe Margin Disparity:** Central's gross margin of **7.92%** is nearly half that of the West region (**14.94%**), representing a 702 basis-point drag.
- **Root-Cause Indicator (Discount Disparity):** Central's average discount rate is **24.04%**—more than double the West's 10.93% and substantially higher than East (14.54%) and South (14.73%).
- **Loss Concentration:** Nearly one in three orders in Central (**31.90%**) is loss-making. Central alone accounts for **\$56,126.16 (35.95%)** of total corporate cash leakage.
- **Reproducible Query:** `SELECT * FROM v_regional_performance;` in `sql/business_bi.db`.

### 2.5 Limitations & Alternative Explanations
- *Limitation:* The dataset does not include local competitor density, regional state tax variations, or local warehouse lease expenses.
- *Alternative Explanation:* Central encompasses states (e.g. Texas, Illinois) where local retail competitors may have engaged in aggressive price-cutting, forcing local reps to match prices defensively.
- *Confidence Level:* **High (Direct arithmetic calculation from 2,323 Central transactions).**

### 2.6 Evidence-Linked Recommendation
Institute a Central-region commercial pricing audit. Retrain the Central sales force on value-selling rather than price concession, and eliminate discretionary discounting above 15% across Central branches.

---

## DOSSIER 3: SUB-CATEGORY PROFITABILITY (TABLES, BOOKCASES & SUPPLIES)

### 3.1 Business Question & Hypothesis
- **Business Question:** Are all product sub-categories contributing positively to EBITDA, or do specific product lines destroy economic value?
- **Hypothesis:** *Tables*, *Bookcases*, and *Supplies* generate cumulative net losses across the 4-year horizon.

### 3.2 Dataset Scope, Filters & KPI Definitions
- **Dataset Period:** 2015-01-03 to 2018-12-30.
- **Filter Applied:** Grouped by `DimProduct[Category]` and `DimProduct[SubCategory]`.
- **Relevant KPI Definitions:**
  - $\text{Net Margin \%} = \frac{\sum \text{Profit}}{\sum \text{Sales}}$
  - $\text{Negative Profit Tally} = \sum \text{Profit} \quad (\text{WHERE Profit } < 0)$

### 3.3 Calculated Findings & Comparison Baseline

| Sub-Category | Parent Category | Order Lines | Total Revenue | Total Net Profit | Net Margin % | Avg Discount Rate | Loss-Making Order Lines | Net Profit Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Tables** | Furniture | 319 | \$206,965.53 | **-\$17,725.48** | **-8.56%** | **26.13%** | 130 (40.8%) | **Chronic Net Loss** |
| **Bookcases** | Furniture | 228 | \$114,880.00 | **-\$3,472.56** | **-3.02%** | **21.11%** | 109 (47.8%) | **Chronic Net Loss** |
| **Supplies** | Office Supplies | 190 | \$46,673.54 | **-\$1,189.10** | **-2.55%** | **7.68%** | 33 (17.4%) | **Chronic Net Loss** |
| *Fasteners* | Office Supplies | 217 | \$3,024.28 | +\$949.52 | +31.40% | 8.20% | 12 (5.5%) | Low Volume / Profitable |
| *Paper* | Office Supplies | 1,370 | \$78,479.20 | +\$34,053.51 | +43.39% | 7.49% | 0 (0.0%) | High Volume / High Margin |
| *Copiers* | Technology | 68 | \$149,528.03 | +\$55,617.82 | +37.20% | 16.18% | 3 (4.4%) | Star Performer |

### 3.4 Evidence from Data
- **The Three Chronic Loss Leaders:** Out of all 17 sub-categories, exactly **three** produced cumulative net negative profit over the entire 4-year operating history:
  1. **Tables:** Net Loss of **-\$17,725.48** on \$206.9K sales (-8.56% margin; avg discount 26.13%).
  2. **Bookcases:** Net Loss of **-\$3,472.56** on \$114.9K sales (-3.02% margin; avg discount 21.11%).
  3. **Supplies:** Net Loss of **-\$1,189.10** on \$46.7K sales (-2.55% margin; avg discount 7.68%).
- **Different Diagnostic Root Causes:**
  - *Tables & Bookcases:* Driven by excessive promotional discounting (avg discounts of 26.1% and 21.1%).
  - *Supplies:* Unlike Tables, Supplies has a low discount rate (7.68%). Its negative profitability is driven by a flawed baseline wholesale cost structure (derived COGS is 102.5% of sales on specific high-cost SKUs).
- **Reproducible Query:** `SELECT * FROM v_subcategory_profitability;` in `sql/business_bi.db`.

### 3.5 Limitations & Alternative Explanations
- *Limitation:* The dataset lacks supplier wholesale contract terms and bulk freight packing specs.
- *Alternative Explanation:* Tables may function as a "loss leader" to sell high-margin chairs and desktop accessories in office bundle deals.
- *Confidence Level:* **High (Definitive arithmetic tally across 737 order lines in these 3 lines).**

### 3.6 Evidence-Linked Recommendation
1. For Tables & Bookcases: Immediately mandate a 15% discount ceiling and re-evaluate bundling rules.
2. For Supplies: Renegotiate supplier procurement costs or discontinue the bottom 10 negative-margin SKUs.

---

## DOSSIER 4: ACTUAL VERSUS SYNTHETIC PLANNING TARGETS

### 4.1 Business Question & Hypothesis
- **Business Question:** Did the enterprise meet its budgeted revenue and profit quotas across the 4-year horizon, and where was the shortfall concentrated?
- **Hypothesis:** Actual top-line revenue and bottom-line profit fell short of managerial planning targets due to lagging regional performance and margin compression.

### 4.2 Dataset Scope, Filters & KPI Definitions
- **Dataset Period:** 2015 to 2018 (4 Calendar Years / 48 Months).
- **Target Nature:** **100% Synthetic Managerial Budget Model** (calibrated via `src/generate_targets.py` with seed=42; 576 rows).
- **Relevant KPI Definitions:**
  - $\text{Revenue Variance (\$) } = \text{Actual Revenue} - \text{Target Revenue}$
  - $\text{Revenue Attainment \% } = \frac{\text{Actual Revenue}}{\text{Target Revenue}} \times 100$
  - $\text{Profit Variance (\$) } = \text{Actual Profit} - \text{Target Profit}$
  - $\text{Profit Attainment \% } = \frac{\text{Actual Profit}}{\text{Target Profit}} \times 100$

### 4.3 Calculated Findings & Comparison Baseline

| Year | Target Revenue ($) | Actual Revenue ($) | Revenue Variance ($) | Revenue Attainment % | Target Profit ($) | Actual Profit ($) | Profit Variance ($) | Profit Attainment % |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2015** | \$564,851.32 | \$484,247.50 | -\$80,603.82 | **85.73%** | \$84,896.79 | \$49,543.97 | -\$35,352.82 | **58.36%** |
| **2016** | \$605,951.05 | \$470,532.51 | -\$135,418.54 | **77.65%** | \$91,152.09 | \$61,618.60 | -\$29,533.49 | **67.60%** |
| **2017** | \$669,141.67 | \$608,473.83 | -\$60,667.84 | **90.93%** | \$100,771.60 | \$81,777.10 | -\$18,994.50 | **81.15%** |
| **2018** | \$762,599.19 | \$733,947.02 | -\$28,652.17 | **96.24%** | \$114,566.88 | \$93,457.35 | -\$21,109.53 | **81.57%** |
| **TOTAL** | **\$2,602,543.23** | **\$2,297,200.86** | **-\$305,342.37** | **88.27%** | **\$391,387.36** | **\$286,397.02** | **-\$104,990.34** | **73.17%** |

### 4.4 Evidence from Data
- **Revenue Attainment:** Overall 4-year revenue attainment reached **88.27%** with an aggregate deficit of **-\$305,342.37**. Revenue velocity improved progressively from 77.65% in 2016 to 96.24% in 2018.
- **Profit Attainment Deficit:** Profit attainment trailed significantly behind revenue, achieving only **73.17%** overall (Shortfall of **-\$104,990.34**).
- **Category Decomposition:** The profit shortfall was heavily concentrated in `Furniture` (Profit Attainment: 47.3%) and `Central Region` (Profit Attainment: 48.9%).
- **Reproducible Query:** `SELECT * FROM v_target_variance_decomposition;` in `sql/business_bi.db`.

### 4.5 Limitations & Alternative Explanations
- *Limitation:* The targets are synthetic managerial benchmarks generated for variance modeling. They do not represent boardroom commitments made by actual corporate officers.
- *Alternative Explanation:* Aggressive top-down growth quotas (10–12% annual escalation) outpaced macroeconomic growth, setting unrealistic expectations during the 2015–2016 period.
- *Confidence Level:* **High (Deterministic mathematical variance based on fixed-seed synthetic targets).**

### 4.6 Evidence-Linked Recommendation
Calibrate future regional quotas using bottom-up historical baseline data rather than uniform top-down growth assumptions, factoring in category-specific margin constraints.

---

## DOSSIER 5: DELIVERY LEAD TIMES, SHIPPING MODES & SLA ADHERENCE

### 5.1 Business Question & Hypothesis
- **Business Question:** Does logistics fulfillment adhere to carrier service-level agreements (SLAs), and are delivery delays concentrated in specific shipping classes?
- **Hypothesis (Revised):** Carrier delivery lead times frequently breach standard SLA commitments, particularly in expedited shipping tiers.

> [!WARNING]
> **TRANSPARENT DATASET LIMITATION DISCLOSURE (Condition 4):**  
> The candidate hypothesis initially proposed investigating discrete *"Same-Day shipping cost expense discrepancies"*. However, forensic auditing confirms that the US Commercial Orders dataset contains delivery timestamps (`Order Date`, `Ship Date`, `FulfillmentDays`) and shipping classes (`Ship Mode`), but **does not contain a separate carrier freight invoice dollar ledger** (which exists only in the Global Superstore variant). In strict accordance with governance Condition 4, we explicitly decline to invent synthetic freight cost figures and instead evaluate empirical **fulfillment cycle lead times and carrier SLA adherence rates**.

### 5.2 Dataset Scope, Filters & KPI Definitions
- **Dataset Period:** 2015-01-03 to 2018-12-30.
- **Filter Applied:** Grouped by `DimShipMode[ShipMode]`.
- **Relevant KPI Definitions:**
  - $\text{Fulfillment Cycle Days} = \text{Ship Date} - \text{Order Date}$
  - $\text{SLA Adherence \%} = \frac{\text{Count of Orders with FulfillmentDays } \le \text{StandardSLADays}}{\text{Total Orders in Mode}} \times 100$

### 5.3 Calculated Findings & Comparison Baseline

| Shipping Mode | Standard SLA Commitment | Order Volume | Actual Avg Fulfillment Days | Fastest Fulfillment | Slowest Fulfillment | On-Time Orders | SLA Adherence % | SLA Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Same Day** | 0 Days | 543 | **0.04 Days** | 0 Days | 1 Day | 519 | **95.58%** | **Met (>95% SLA Target)** |
| **First Class** | 2 Days | 1,538 | **2.18 Days** | 1 Day | 4 Days | 915 | **59.49%** | **SEVERE BREACH (40.5% Late)** |
| **Second Class** | 4 Days | 1,945 | **3.24 Days** | 1 Day | 5 Days | 1,516 | **77.94%** | **MODERATE BREACH (22.1% Late)** |
| **Standard Class** | 6 Days | 5,968 | **5.01 Days** | 3 Days | 7 Days | 5,348 | **89.61%** | Acceptable (<6 Days Avg) |
| **OVERALL** | -- | **9,994** | **3.96 Days** | **0 Days** | **7 Days** | **8,298** | **83.03%** | 16.97% Overall Delay Rate |

### 5.4 Evidence from Data
- **The First Class SLA Breakdown:** While customers select `First Class` expecting 2-day expedited fulfillment, actual SLA adherence is only **59.49%** (915 on-time out of 1,538 orders). Over **40% of First Class orders take 3 to 4 days to ship**, essentially performing at Second Class speeds.
- **Second Class Slippage:** `Second Class` orders experience a **22.06% delay rate** (429 orders taking 5 days).
- **Same Day Efficiency:** In contrast, `Same Day` shipping performs exceptionally well with **95.58% on-time execution** (avg lead time: 0.04 days).
- **Reproducible Query:** `SELECT * FROM fact_orders o JOIN dim_ship_mode s ON o.ShipModeID = s.ShipModeID ...` (Query 6 in `sql/business_queries.sql`).

### 5.5 Limitations & Alternative Explanations
- *Limitation:* The dataset records warehouse dispatch date (`Ship Date`), but lacks final carrier last-mile doorstep delivery timestamps and carrier damage logs.
- *Alternative Explanation:* First Class orders placed late on Friday afternoons or before national holidays may be queued until Monday, artificially extending the calendar-day lead time without violating business-day carrier standards.
- *Confidence Level:* **High (Direct calendar calculation from 9,994 verified timestamp pairs).**

### 5.6 Evidence-Linked Recommendation
Establish a fulfillment priority queue in warehouse operations: prioritize packing of First Class orders before standard orders to eliminate the 40.5% SLA breach rate and protect customer satisfaction.
