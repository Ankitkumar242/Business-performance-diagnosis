# POWER BI 5-PAGE ENTERPRISE DASHBOARD BUILD GUIDE
## Business Performance Diagnosis & Decision Intelligence Platform

**Target Audience:** Power BI Developers, BI Analysts, and Management Reporting Leads  
**Target Application:** Microsoft Power BI Desktop (Windows 11 Compatible)  
**Report Canvas Standard:** 16:9 Widescreen (1280 $\times$ 720 px or 1920 $\times$ 1080 px)  
**Color Palette Standard:** Accessible Corporate Theme: Deep Navy (`#0f4c81`), Steel Blue (`#4682b4`), Emerald Green (`#2ca02c`), Amber Warning (`#ff7f0e`), Crimson Alert (`#d62728`), Light Background (`#f8f9fa`).  

> [!NOTE]
> **PBIX GENERATION & ENVIRONMENT DISCLOSURE (Condition 8):**  
> Microsoft Power BI Desktop `.pbix` files are proprietary binary packages containing internal SQLite/Analysis Services metadata that cannot be natively compiled head-less via command-line scripts without external COM automation or GUI execution. Therefore, this project provides the **complete verified CSV data model pack** in `data/processed/`, **validated DAX library**, and **visual-by-visual construction blueprint** so that any analyst can assemble, validate, and publish the identical report in Power BI Desktop on Windows 11 within 15 minutes.

---

## 1. STEP-BY-STEP WINDOWS 11 POWER BI DESKTOP SETUP INSTRUCTIONS

### Step 1: Open Power BI Desktop & Load Processed CSVs
1. Launch **Microsoft Power BI Desktop** on Windows 11.
2. Click **Home $\rightarrow$ Get Data $\rightarrow$ Text/CSV**.
3. Navigate to the project directory:  
   `C:\Users\ankit\OneDrive\Desktop\Business performance diagnosis\data\processed\`
4. Sequentially import all 7 star-schema files:
   - `fact_orders.csv`
   - `fact_targets.csv`
   - `dim_date.csv`
   - `dim_customer.csv`
   - `dim_product.csv`
   - `dim_geography.csv`
   - `dim_ship_mode.csv`
5. Click **Transform Data** to open Power Query Editor, verify data types as documented in `powerbi/data_model.md`, and click **Close & Apply**.

### Step 2: Establish Star-Schema Relationships
1. In Power BI Desktop, switch to the **Model View** (left navigation bar, third icon).
2. Wire the 1-to-Many single-direction relationships:
   - `DimDate[DateKey]` $\rightarrow$ `FactOrders[OrderDateKey]` (Active, 1-to-Many, Single)
   - `DimDate[DateKey]` $\rightarrow$ `FactOrders[ShipDateKey]` (Inactive, 1-to-Many, Single)
   - `DimDate[DateKey]` $\rightarrow$ `FactTargets[TargetDateKey]` (Active, 1-to-Many, Single)
   - `DimCustomer[CustomerID]` $\rightarrow$ `FactOrders[CustomerID]` (Active, 1-to-Many, Single)
   - `DimProduct[ProductID]` $\rightarrow$ `FactOrders[ProductID]` (Active, 1-to-Many, Single)
   - `DimGeography[GeographyID]` $\rightarrow$ `FactOrders[GeographyID]` (Active, 1-to-Many, Single)
   - `DimShipMode[ShipModeID]` $\rightarrow$ `FactOrders[ShipModeID]` (Active, 1-to-Many, Single)
3. Select `DimDate` table $\rightarrow$ Table Tools $\rightarrow$ **Mark as Date Table** $\rightarrow$ Date Column: `FullDate`.

### Step 3: Create the Dedicated `_Measures` Calculation Table
1. On the **Home** tab, click **Enter Data**.
2. Name the table `_Measures` and click **Load**.
3. Create the explicit measures defined in `powerbi/dax_measures.md` by right-clicking `_Measures` $\rightarrow$ **New Measure**.
4. Delete the empty default column `Column1` so that `_Measures` floats to the very top of your Fields pane with a calculator icon.

---

## 2. REPORT PAGE SPECIFICATIONS (5 PAGES)

### PAGE 1: EXECUTIVE OVERVIEW (The C-Suite Cockpit)
- **Primary Business Question:** Is the business achieving its overall top-line and bottom-line targets, and what is the multi-year monthly trajectory?
- **Top Slicer Bar:**
  - Slicer 1: `DimDate[Year]` (Tile / Horizontal buttons: 2015, 2016, 2017, 2018).
  - Slicer 2: `DimGeography[Region]` (Dropdown: Central, East, South, West).
  - Slicer 3: `DimProduct[Category]` (Dropdown: Furniture, Office Supplies, Technology).

- **Visual 1–4: Executive KPI Cards (Row 1 across canvas):**
  - **Card 1 (Total Revenue):** Measure `[Total Sales]`, formatted as Currency `\$#,##0`. Subtitle: `[Sales YoY Growth %]`.
  - **Card 2 (Total Net Profit):** Measure `[Total Profit]`, formatted as Currency `\$#,##0`.
  - **Card 3 (Gross Profit Margin %):** Measure `[Gross Margin %]`, formatted as Percentage `0.0%`. Conditional text color bound to measure `[Margin Health Color]`.
  - **Card 4 (Revenue Quota Attainment):** Measure `[Revenue Attainment %]`, formatted as Percentage `0.0%`. Conditional background color bound to `[KPI Attainment Alert Color]`.

- **Visual 5: Monthly Revenue vs. Target Trajectory (Main Chart, Left):**
  - **Visual Type:** Clustered Column and Line Chart.
  - **Shared Axis (X-axis):** `DimDate[YearMonth]`.
  - **Column Values (Bars):** `[Total Sales]` (Color: Steel Blue `#4682b4`).
  - **Line Values (Line):** `[Target Revenue]` (Color: Dark Amber `#ff7f0e`, dashed line).
  - **Tooltip:** `[Gross Margin %]`, `[Revenue Variance $]`.

- **Visual 6: Regional Revenue & Margin Distribution (Right Top):**
  - **Visual Type:** Donut Chart or Horizontal Bar Chart.
  - **Category / Axis:** `DimGeography[Region]`.
  - **Values:** `[Total Sales]`.
  - **Tooltips:** `[Gross Margin %]`, `[Total Profit]`, `[Regional Share of Portfolio %]`.

- **Visual 7: Top 5 Outperforming vs. Bottom 5 Underperforming Sub-Categories (Right Bottom):**
  - **Visual Type:** Clustered Bar Chart.
  - **Axis (Y-axis):** `DimProduct[SubCategory]`.
  - **Values (X-axis):** `[Total Profit]`.
  - **Conditional Color:** Green if `[Total Profit] >= 0`, Red if `[Total Profit] < 0`. Highlights chronic losses in *Tables* and *Bookcases*.

---

### PAGE 2: BUSINESS PERFORMANCE & TARGET VARIANCE DIAGNOSIS
- **Primary Business Question:** Where are the exact dollar shortfalls against budgeted quotas across product lines and operating regions?
- **Visual 1: Target-to-Actual Variance Decomposition Matrix (Top Half):**
  - **Visual Type:** Matrix Visual.
  - **Rows:** `DimGeography[Region]`, expandable to `DimProduct[Category]` and `DimProduct[SubCategory]`.
  - **Columns:** `DimDate[Year]`.
  - **Values:**
    1. `[Target Revenue]` (\$#,##0)
    2. `[Total Sales]` (\$#,##0)
    3. `[Revenue Variance $]` (Conditional background: Red for deficits $< 0$, Green for surplus $> 0$).
    4. `[Revenue Attainment %]` (Formatted as `0.0%`).
    5. `[Target Profit]` (\$#,##0).
    6. `[Total Profit]` (\$#,##0).
    7. `[Profit Variance $]`.
    8. `[Margin Variance %]`.

- **Visual 2: Revenue Variance Bridge / Waterfall Chart (Bottom Left):**
  - **Visual Type:** Waterfall Chart.
  - **Category:** `DimGeography[Region]`.
  - **Breakdown:** `DimProduct[Category]`.
  - **Y-axis:** `[Revenue Variance $]`.
  - **Business Purpose:** Visually demonstrates how Central region and Furniture category create the largest negative drag on target attainment.

- **Visual 3: Month-over-Month Velocity Momentum (Bottom Right):**
  - **Visual Type:** Line Chart with Trailing 3-Month Moving Average.
  - **X-axis:** `DimDate[YearMonth]`.
  - **Y-axis:** `[Sales MoM Growth %]`.
  - **Reference Line:** 0.0% Growth Line.

- **Interactivity & Drill-Through:**
  - Configure Drill-through on `DimGeography[Region]` leading to a dedicated State and City breakdown page.

---

### PAGE 3: PROFITABILITY & COST ANALYSIS
- **Primary Business Question:** Where is profit being destroyed, and what is the exact financial drag of deep discounting?
- **Visual 1: Profit Margin vs. Discount Depth Scatter Analysis (Top Left):**
  - **Visual Type:** Scatter Chart.
  - **X-axis:** `FactOrders[Discount]` (Formatted as Percentage `0%`).
  - **Y-axis:** `FactOrders[ProfitMarginPct]` (Formatted as Percentage `0.0%`).
  - **Legend:** `FactOrders[DiscountBracket]`.
  - **Size:** `FactOrders[Sales]`.
  - **Reference Line:** Horizontal line at $Y = 0.0\%$ (Break-even).
  - **Business Insight:** Instantly reveals the dense cluster of orders with discounts $>20\%$ plunging below the zero-margin line.

- **Visual 2: Sub-Category Profit Erosion Leaderboard (Top Right):**
  - **Visual Type:** Horizontal Bar Chart (Sorted ascending by profit).
  - **Y-axis:** `DimProduct[SubCategory]`.
  - **X-axis:** `[Total Profit]`.
  - **Data Labels:** Displays negative values clearly in red callout boxes (*Tables*: -\$17.7K, *Bookcases*: -\$3.5K, *Supplies*: -\$1.2K).

- **Visual 3: Discount Bracket Margin Collapse Table (Bottom Left):**
  - **Visual Type:** Table Visual.
  - **Columns:**
    1. `FactOrders[DiscountBracket]`
    2. `[Distinct Orders]`
    3. `[Total Sales]`
    4. `[Total Profit]`
    5. `[Gross Margin %]`
    6. `[Average Discount Rate]`
    7. `[Cash Leakage $]`
    8. `[Loss-Making Share %]`
  - **Conditional Heatmap:** Formats `[Gross Margin %]` from Green (0% discount: 29.9%) to Dark Red (>40% discount: -85.1%).

- **Visual 4: Cost Structure & Derived COGS Composition (Bottom Right):**
  - **Visual Type:** 100% Stacked Bar Chart.
  - **Y-axis:** `DimProduct[Category]`.
  - **X-axis:** `[Total COGS]` and `[Total Profit]`.
  - **Business Insight:** Illustrates that Furniture consumes 91.3% of revenue in COGS, leaving only an 8.7% operating margin.

---

### PAGE 4: TRENDS & ROOT-CAUSE INVESTIGATION
- **Primary Business Question:** Are delivery lead times and customer returns contributing to margin erosion and regional underperformance?
- **Visual 1: Carrier SLA Compliance & Fulfillment Lead Times (Top Half):**
  - **Visual Type:** Grouped Column and Line Chart.
  - **X-axis:** `DimShipMode[ShipMode]`.
  - **Column Values (Left Y-axis):** `[SLA Adherence %]` (Target reference line at 95.0%).
  - **Line Values (Right Y-axis):** `[Average Fulfillment Days]`.
  - **Tooltip:** `DimShipMode[StandardSLADays]`, `[Distinct Orders]`.

- **Visual 2: Customer Return Rate by Product Category & Region (Bottom Left):**
  - **Visual Type:** Clustered Bar Chart.
  - **Axis:** `DimGeography[Region]`.
  - **Legend:** `DimProduct[Category]`.
  - **Values:** `[Return Rate %]`.
  - **Finding:** Highlights whether returned orders are concentrated in specific problematic sub-categories.

- **Visual 3: Key Influencers / Decomposition Tree Visual (Bottom Right):**
  - **Visual Type:** Decomposition Tree (AI Visual in Power BI).
  - **Analyze:** `[Total Profit]`.
  - **Explain By:** `DimGeography[Region]`, `DimProduct[Category]`, `FactOrders[DiscountBracket]`, `DimCustomer[Segment]`.
  - **Business Value:** Enables an interactive drill-down path explaining exactly which combination of factors yields negative profit.

---

### PAGE 5: DECISION & ACTION TRACKING MATRIX
- **Primary Business Question:** What prioritized interventions should commercial management take, and what is the quantified dollar upside?
- **Visual 1: Remediation Decision Matrix (Top Half):**
  - **Visual Type:** Table Visual.
  - **Columns:**
    1. Finding ID (`F-01` to `F-05`)
    2. Problem Description
    3. Impact Level (High / Medium / Low)
    4. Effort Level (Low / Moderate / High)
    5. Responsible Business Owner (e.g., VP Pricing, Central GM, Merchandising Lead)
    6. Historical Observed Leakage (\$)
    7. Proposed Intervention
    8. Monitoring KPI
    9. Quarterly Review Date

- **Visual 2: Interactive "What-If" Discount Cap Simulator (Bottom Left):**
  - **Visual Type:** What-If Parameter Slider: "Maximum Discount Allowed (%)" (0% to 50%, increment 5%).
  - **Dynamic Measure:**
    ```dax
    Simulated Recovered Margin $ = 
    VAR CapRate = 'Discount Cap Parameter'[Discount Cap Parameter Value] / 100.0
    RETURN
    CALCULATE(
        SUMX(
            FILTER(FactOrders, FactOrders[Discount] > CapRate),
            FactOrders[Sales] * (FactOrders[Discount] - CapRate)
        )
    )
    ```
  - **Business Purpose:** Allows executive leadership to interactively model the bottom-line dollar impact of enforcing a 20% discount ceiling.

- **Visual 3: Monthly Operational Governance Scorecard (Bottom Right):**
  - **Visual Type:** KPI Multi-row Card displaying Leading & Lagging Indicators:
    - Leading KPI 1: Orders with Discount $>20\%$ (Target: $< 5\%$).
    - Leading KPI 2: Fulfillment SLA Adherence (Target: $\ge 95\%$).
    - Lagging KPI 1: Enterprise Gross Margin (Target: $\ge 15.0\%$).
    - Lagging KPI 2: Quarterly Target Quota Attainment (Target: $\ge 100\%$).
