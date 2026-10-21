-- ======================================================================
-- ADVANCED BUSINESS QUERIES CATALOG
-- Project: Business Performance Diagnosis & Decision Intelligence Platform
-- Target Database: SQLite 3 (sql/business_bi.db)
-- Features: CTEs, Window Functions (LAG, RANK, ROW_NUMBER, SUM OVER),
--           Division-by-zero protection, First-month boundary handling.
-- ======================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------
-- QUERY 1: Month-over-Month (MoM) Revenue & Profit Velocity
-- Business Question: How has revenue and profit velocity evolved month-over-month?
-- Analytical Method: LAG() window function across chronological timeline.
-- Boundary Handling: First month (2015-01) has NULL previous revenue -- explicitly
--                    handled using CASE and NULLIF to prevent division by zero.
-- ----------------------------------------------------------------------
WITH monthly_metrics AS (
    SELECT
        d.YearMonth,
        d.Year,
        d.Month,
        ROUND(SUM(o.Sales), 2) AS CurrentMonthRevenue,
        ROUND(SUM(o.Profit), 2) AS CurrentMonthProfit,
        ROUND(SUM(o.Profit) * 1.0 / NULLIF(SUM(o.Sales), 0), 4) AS GrossMarginPct
    FROM fact_orders o
    JOIN dim_date d ON o.OrderDateKey = d.DateKey
    GROUP BY d.YearMonth, d.Year, d.Month
),
lagged_metrics AS (
    SELECT
        YearMonth,
        Year,
        Month,
        CurrentMonthRevenue,
        CurrentMonthProfit,
        GrossMarginPct,
        LAG(CurrentMonthRevenue, 1) OVER (ORDER BY YearMonth) AS PrevMonthRevenue,
        LAG(CurrentMonthProfit, 1) OVER (ORDER BY YearMonth) AS PrevMonthProfit
    FROM monthly_metrics
)
SELECT
    YearMonth,
    CurrentMonthRevenue,
    COALESCE(PrevMonthRevenue, 0.0) AS PrevMonthRevenue,
    ROUND(CurrentMonthRevenue - COALESCE(PrevMonthRevenue, CurrentMonthRevenue), 2) AS MoM_Revenue_Change,
    CASE
        WHEN PrevMonthRevenue IS NULL THEN 0.0
        WHEN PrevMonthRevenue = 0 THEN 0.0
        ELSE ROUND(((CurrentMonthRevenue - PrevMonthRevenue) * 100.0) / PrevMonthRevenue, 2)
    END AS MoM_Revenue_Growth_Pct,
    CurrentMonthProfit,
    COALESCE(PrevMonthProfit, 0.0) AS PrevMonthProfit,
    ROUND(CurrentMonthProfit - COALESCE(PrevMonthProfit, CurrentMonthProfit), 2) AS MoM_Profit_Change,
    CASE
        WHEN PrevMonthProfit IS NULL THEN 0.0
        WHEN PrevMonthProfit = 0 THEN 0.0
        ELSE ROUND(((CurrentMonthProfit - PrevMonthProfit) * 100.0) / ABS(PrevMonthProfit), 2)
    END AS MoM_Profit_Growth_Pct,
    GrossMarginPct
FROM lagged_metrics
ORDER BY YearMonth;

-- ----------------------------------------------------------------------
-- QUERY 2: Product Sub-Category Performance & Pareto Contribution Ranking
-- Business Question: What is the cumulative revenue and profit share of each
--                    sub-category, and which ones generate 80% of total revenue?
-- Analytical Method: Window functions RANK() and running cumulative SUM() OVER().
-- ----------------------------------------------------------------------
WITH subcat_totals AS (
    SELECT
        p.Category,
        p.SubCategory,
        ROUND(SUM(o.Sales), 2) AS SubCatRevenue,
        ROUND(SUM(o.Profit), 2) AS SubCatProfit,
        ROUND(SUM(o.Profit) * 1.0 / NULLIF(SUM(o.Sales), 0), 4) AS MarginPct
    FROM fact_orders o
    JOIN dim_product p ON o.ProductID = p.ProductID
    GROUP BY p.Category, p.SubCategory
),
grand_total AS (
    SELECT SUM(SubCatRevenue) AS TotalPortfolioRevenue FROM subcat_totals
)
SELECT
    RANK() OVER (ORDER BY s.SubCatRevenue DESC) AS RevenueRank,
    s.Category,
    s.SubCategory,
    s.SubCatRevenue,
    s.SubCatProfit,
    s.MarginPct,
    ROUND((s.SubCatRevenue * 100.0) / g.TotalPortfolioRevenue, 2) AS ShareOfTotalRevenuePct,
    ROUND(
        SUM(s.SubCatRevenue) OVER (ORDER BY s.SubCatRevenue DESC) * 100.0 / g.TotalPortfolioRevenue,
        2
    ) AS CumulativeRevenuePct,
    CASE
        WHEN SUM(s.SubCatRevenue) OVER (ORDER BY s.SubCatRevenue DESC) * 1.0 / g.TotalPortfolioRevenue <= 0.80
        THEN 'Core Driver (Top 80%)'
        ELSE 'Long Tail (Bottom 20%)'
    END AS ParetoTier
FROM subcat_totals s
CROSS JOIN grand_total g
ORDER BY RevenueRank;

-- ----------------------------------------------------------------------
-- QUERY 3: Regional Performance & Margin Drag Ranking
-- Business Question: Which regions drag corporate profitability down the most?
-- Analytical Method: DENSE_RANK() by profit margin and cash leakage aggregation.
-- ----------------------------------------------------------------------
SELECT
    DENSE_RANK() OVER (ORDER BY ROUND(SUM(o.Profit) * 1.0 / NULLIF(SUM(o.Sales), 0), 4) ASC) AS MarginRankWorstToBest,
    g.Region,
    ROUND(SUM(o.Sales), 2) AS TotalRevenue,
    ROUND(SUM(o.Profit), 2) AS TotalProfit,
    ROUND(SUM(o.Profit) * 1.0 / NULLIF(SUM(o.Sales), 0), 4) AS GrossMarginPct,
    ROUND(AVG(o.Discount), 4) AS AvgDiscountRate,
    SUM(o.IsLossMaking) AS LossMakingOrdersCount,
    ROUND(SUM(o.IsLossMaking) * 100.0 / COUNT(*), 2) AS LossMakingOrderPct,
    ROUND(SUM(CASE WHEN o.Profit < 0 THEN ABS(o.Profit) ELSE 0 END), 2) AS TotalCashLeakageDollar
FROM fact_orders o
JOIN dim_geography g ON o.GeographyID = g.GeographyID
GROUP BY g.Region
ORDER BY MarginRankWorstToBest;

-- ----------------------------------------------------------------------
-- QUERY 4: Top 3 Loss-Making Products in Each Region
-- Business Question: Exactly which SKUs are driving the highest absolute losses
--                    in each regional operating theater?
-- Analytical Method: ROW_NUMBER() OVER (PARTITION BY Region ORDER BY TotalProfit ASC).
-- ----------------------------------------------------------------------
WITH product_regional_losses AS (
    SELECT
        g.Region,
        p.ProductID,
        p.Category,
        p.SubCategory,
        p.ProductName,
        ROUND(SUM(o.Sales), 2) AS RegionalSales,
        ROUND(SUM(o.Profit), 2) AS RegionalProfit,
        ROUND(AVG(o.Discount), 4) AS AvgDiscountGiven,
        SUM(o.Quantity) AS UnitsSold,
        ROW_NUMBER() OVER (
            PARTITION BY g.Region
            ORDER BY SUM(o.Profit) ASC
        ) AS LossRankInRegion
    FROM fact_orders o
    JOIN dim_geography g ON o.GeographyID = g.GeographyID
    JOIN dim_product p ON o.ProductID = p.ProductID
    GROUP BY g.Region, p.ProductID, p.Category, p.SubCategory, p.ProductName
    HAVING SUM(o.Profit) < 0
)
SELECT
    Region,
    LossRankInRegion,
    Category,
    SubCategory,
    ProductID,
    ProductName,
    RegionalSales,
    RegionalProfit,
    AvgDiscountGiven,
    UnitsSold
FROM product_regional_losses
WHERE LossRankInRegion <= 3
ORDER BY Region, LossRankInRegion;

-- ----------------------------------------------------------------------
-- QUERY 5: Annual Target Achievement & Budget Deficit Analysis
-- Business Question: Did the company hit annual targets, and what was the budget deficit?
-- Analytical Method: Aggregates target vs actual by calendar year.
-- ----------------------------------------------------------------------
WITH actual_annual AS (
    SELECT
        d.Year,
        ROUND(SUM(o.Sales), 2) AS ActualRevenue,
        ROUND(SUM(o.Profit), 2) AS ActualProfit
    FROM fact_orders o
    JOIN dim_date d ON o.OrderDateKey = d.DateKey
    GROUP BY d.Year
),
target_annual AS (
    SELECT
        Year,
        ROUND(SUM(TargetRevenue), 2) AS TargetRevenue,
        ROUND(SUM(TargetProfit), 2) AS TargetProfit
    FROM fact_targets
    GROUP BY Year
)
SELECT
    t.Year,
    t.TargetRevenue,
    a.ActualRevenue,
    ROUND(a.ActualRevenue - t.TargetRevenue, 2) AS RevenueVarianceDollar,
    ROUND((a.ActualRevenue * 100.0) / NULLIF(t.TargetRevenue, 0), 2) AS RevenueAchievementPct,
    t.TargetProfit,
    a.ActualProfit,
    ROUND(a.ActualProfit - t.TargetProfit, 2) AS ProfitVarianceDollar,
    ROUND((a.ActualProfit * 100.0) / NULLIF(t.TargetProfit, 0), 2) AS ProfitAchievementPct,
    ROUND(a.ActualProfit * 1.0 / NULLIF(a.ActualRevenue, 0), 4) AS ActualMarginPct,
    ROUND(t.TargetProfit * 1.0 / NULLIF(t.TargetRevenue, 0), 4) AS TargetMarginPct
FROM target_annual t
JOIN actual_annual a ON t.Year = a.Year
ORDER BY t.Year;

-- ----------------------------------------------------------------------
-- QUERY 6: Carrier Shipping SLA Adherence & Average Fulfillment Cycle Days
-- Business Question: Are orders delivered on schedule according to carrier SLA?
-- Analytical Method: Evaluates actual fulfillment days against standard SLA days.
-- ----------------------------------------------------------------------
SELECT
    s.ShipMode,
    s.StandardSLADays AS CarrierSLADays,
    COUNT(o.RowID) AS TotalOrdersShipped,
    ROUND(AVG(o.FulfillmentDays), 2) AS ActualAvgFulfillmentDays,
    MIN(o.FulfillmentDays) AS FastestFulfillmentDays,
    MAX(o.FulfillmentDays) AS SlowestFulfillmentDays,
    SUM(CASE WHEN o.FulfillmentDays <= s.StandardSLADays THEN 1 ELSE 0 END) AS OnTimeOrders,
    ROUND(
        SUM(CASE WHEN o.FulfillmentDays <= s.StandardSLADays THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) AS SLA_Adherence_Pct
FROM fact_orders o
JOIN dim_ship_mode s ON o.ShipModeID = s.ShipModeID
GROUP BY s.ShipMode, s.StandardSLADays
ORDER BY s.StandardSLADays ASC;
