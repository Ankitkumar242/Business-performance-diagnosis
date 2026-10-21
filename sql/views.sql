-- ======================================================================
-- PRODUCTION BI ANALYTICAL VIEWS
-- Project: Business Performance Diagnosis & Decision Intelligence Platform
-- Target Database: SQLite 3 (sql/business_bi.db)
-- ======================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------
-- VIEW 1: v_monthly_financials
-- Business Meaning: High-level financial trend and monthly velocity.
-- KPI Formulas:
--   TotalRevenue    = SUM(Sales)
--   TotalProfit     = SUM(Profit)
--   GrossMarginPct  = SUM(Profit) / SUM(Sales)
--   AvgOrderValue   = SUM(Sales) / COUNT(DISTINCT OrderID)
--   AvgFulfillmentDays = AVG(FulfillmentDays)
-- ----------------------------------------------------------------------
DROP VIEW IF EXISTS v_monthly_financials;
CREATE VIEW v_monthly_financials AS
SELECT
    d.Year,
    d.Month,
    d.YearMonth,
    d.MonthName,
    COUNT(DISTINCT o.OrderID) AS TotalOrders,
    COUNT(o.RowID) AS TotalOrderLines,
    ROUND(SUM(o.Sales), 2) AS TotalRevenue,
    ROUND(SUM(o.COGS), 2) AS TotalCOGS,
    ROUND(SUM(o.Profit), 2) AS TotalProfit,
    ROUND(SUM(o.Profit) * 1.0 / NULLIF(SUM(o.Sales), 0), 4) AS GrossMarginPct,
    ROUND(SUM(o.Sales) * 1.0 / NULLIF(COUNT(DISTINCT o.OrderID), 0), 2) AS AvgOrderValue,
    SUM(o.Quantity) AS TotalQuantity,
    ROUND(AVG(o.Discount), 4) AS AvgDiscount,
    ROUND(AVG(o.FulfillmentDays), 2) AS AvgFulfillmentDays
FROM fact_orders o
JOIN dim_date d ON o.OrderDateKey = d.DateKey
GROUP BY d.Year, d.Month, d.YearMonth, d.MonthName
ORDER BY d.YearMonth;

-- ----------------------------------------------------------------------
-- VIEW 2: v_target_variance_decomposition
-- Business Meaning: Reconciles monthly budget quotas against actual performance
--                   by YearMonth, Region, and Product Category.
-- KPI Formulas:
--   RevenueVarianceDollar   = ActualRevenue - TargetRevenue
--   RevenueAchievementPct  = (ActualRevenue / TargetRevenue) * 100
--   ProfitVarianceDollar    = ActualProfit - TargetProfit
--   ProfitAchievementPct   = (ActualProfit / TargetProfit) * 100
--   MarginVariancePct      = ActualMarginPct - TargetMarginPct
-- ----------------------------------------------------------------------
DROP VIEW IF EXISTS v_target_variance_decomposition;
CREATE VIEW v_target_variance_decomposition AS
WITH actuals AS (
    SELECT
        d.YearMonth,
        g.Region,
        p.Category,
        ROUND(SUM(o.Sales), 2) AS ActualRevenue,
        ROUND(SUM(o.Profit), 2) AS ActualProfit,
        COUNT(o.RowID) AS OrderLineCount
    FROM fact_orders o
    JOIN dim_date d ON o.OrderDateKey = d.DateKey
    JOIN dim_geography g ON o.GeographyID = g.GeographyID
    JOIN dim_product p ON o.ProductID = p.ProductID
    GROUP BY d.YearMonth, g.Region, p.Category
)
SELECT
    t.YearMonth,
    t.Year,
    t.Month,
    t.Region,
    t.Category,
    ROUND(t.TargetRevenue, 2) AS TargetRevenue,
    COALESCE(a.ActualRevenue, 0.0) AS ActualRevenue,
    ROUND(COALESCE(a.ActualRevenue, 0.0) - t.TargetRevenue, 2) AS RevenueVarianceDollar,
    ROUND(COALESCE(a.ActualRevenue, 0.0) * 100.0 / NULLIF(t.TargetRevenue, 0), 2) AS RevenueAchievementPct,
    ROUND(t.TargetProfit, 2) AS TargetProfit,
    COALESCE(a.ActualProfit, 0.0) AS ActualProfit,
    ROUND(COALESCE(a.ActualProfit, 0.0) - t.TargetProfit, 2) AS ProfitVarianceDollar,
    ROUND(COALESCE(a.ActualProfit, 0.0) * 100.0 / NULLIF(t.TargetProfit, 0), 2) AS ProfitAchievementPct,
    ROUND(COALESCE(a.ActualProfit, 0.0) * 1.0 / NULLIF(a.ActualRevenue, 0), 4) AS ActualMarginPct,
    ROUND(t.TargetMarginPct, 4) AS TargetMarginPct,
    ROUND(
        (COALESCE(a.ActualProfit, 0.0) * 1.0 / NULLIF(a.ActualRevenue, 0)) - t.TargetMarginPct,
        4
    ) AS MarginVariancePct,
    COALESCE(a.OrderLineCount, 0) AS OrderLineCount
FROM fact_targets t
LEFT JOIN actuals a
    ON t.YearMonth = a.YearMonth
    AND t.Region = a.Region
    AND t.Category = a.Category
ORDER BY t.YearMonth, t.Region, t.Category;

-- ----------------------------------------------------------------------
-- VIEW 3: v_regional_performance
-- Business Meaning: Evaluates geographic performance, customer density,
--                   and regional profit leakage.
-- KPI Formulas:
--   GrossMarginPct  = SUM(Profit) / SUM(Sales)
--   LossMakingPct   = (SUM(IsLossMaking) / COUNT(*)) * 100
--   CashLeakage     = SUM(ABS(Profit)) WHERE Profit < 0
--   ReturnRatePct   = (SUM(IsReturned) / COUNT(*)) * 100
-- ----------------------------------------------------------------------
DROP VIEW IF EXISTS v_regional_performance;
CREATE VIEW v_regional_performance AS
SELECT
    g.Region,
    COUNT(DISTINCT o.OrderID) AS DistinctOrders,
    COUNT(DISTINCT o.CustomerID) AS DistinctCustomers,
    COUNT(DISTINCT g.State) AS ActiveStates,
    COUNT(DISTINCT g.City) AS ActiveCities,
    ROUND(SUM(o.Sales), 2) AS TotalRevenue,
    ROUND(SUM(o.Profit), 2) AS TotalProfit,
    ROUND(SUM(o.Profit) * 1.0 / NULLIF(SUM(o.Sales), 0), 4) AS GrossMarginPct,
    ROUND(AVG(o.Discount), 4) AS AvgDiscount,
    SUM(o.IsLossMaking) AS LossMakingTransactions,
    ROUND(SUM(o.IsLossMaking) * 100.0 / COUNT(*), 2) AS LossMakingSharePct,
    ROUND(SUM(CASE WHEN o.Profit < 0 THEN ABS(o.Profit) ELSE 0 END), 2) AS CashLeakageDollar,
    SUM(o.IsReturned) AS ReturnedOrderLines,
    ROUND(SUM(o.IsReturned) * 100.0 / COUNT(*), 2) AS ReturnRatePct,
    ROUND(AVG(o.FulfillmentDays), 2) AS AvgFulfillmentDays
FROM fact_orders o
JOIN dim_geography g ON o.GeographyID = g.GeographyID
GROUP BY g.Region
ORDER BY TotalRevenue DESC;

-- ----------------------------------------------------------------------
-- VIEW 4: v_subcategory_profitability
-- Business Meaning: Identifies chronic loss-making lines vs high-margin stars.
-- KPI Formulas:
--   ProfitStatus: Categorization into Loss-Making (<0), Low (<10%), or Healthy (>=10%)
--   NegativeProfitTally: Cumulative dollar deficit produced by sub-category
-- ----------------------------------------------------------------------
DROP VIEW IF EXISTS v_subcategory_profitability;
CREATE VIEW v_subcategory_profitability AS
SELECT
    p.Category,
    p.SubCategory,
    COUNT(o.RowID) AS TotalOrderLines,
    SUM(o.Quantity) AS TotalUnitsSold,
    ROUND(SUM(o.Sales), 2) AS TotalRevenue,
    ROUND(SUM(o.Profit), 2) AS TotalProfit,
    ROUND(SUM(o.Profit) * 1.0 / NULLIF(SUM(o.Sales), 0), 4) AS GrossMarginPct,
    ROUND(AVG(o.Discount), 4) AS AvgDiscountRate,
    ROUND(MAX(o.Discount), 4) AS MaxDiscountGiven,
    SUM(o.IsLossMaking) AS LossMakingLines,
    ROUND(SUM(o.IsLossMaking) * 100.0 / COUNT(*), 2) AS LossMakingLinePct,
    ROUND(SUM(CASE WHEN o.Profit < 0 THEN o.Profit ELSE 0 END), 2) AS NegativeProfitTally,
    CASE
        WHEN SUM(o.Profit) < 0 THEN 'Loss-Making Sub-Category'
        WHEN (SUM(o.Profit) * 1.0 / NULLIF(SUM(o.Sales), 0)) < 0.10 THEN 'Low Margin (<10%)'
        ELSE 'Healthy Margin (>=10%)'
    END AS ProfitabilityTier
FROM fact_orders o
JOIN dim_product p ON o.ProductID = p.ProductID
GROUP BY p.Category, p.SubCategory
ORDER BY TotalProfit ASC;

-- ----------------------------------------------------------------------
-- VIEW 5: v_discount_bracket_margin_leakage
-- Business Meaning: Proof of discount elasticity and margin collapse.
-- KPI Formulas:
--   LossMakingRatePct = (Count of Loss-Making Orders / Total Orders in Bracket) * 100
--   CashLeakageDollar = Total dollar losses from negative-profit orders
-- ----------------------------------------------------------------------
DROP VIEW IF EXISTS v_discount_bracket_margin_leakage;
CREATE VIEW v_discount_bracket_margin_leakage AS
SELECT
    o.DiscountBracket,
    COUNT(o.RowID) AS TotalTransactions,
    SUM(o.Quantity) AS TotalQuantity,
    ROUND(SUM(o.Sales), 2) AS TotalRevenue,
    ROUND(SUM(o.Profit), 2) AS TotalProfit,
    ROUND(SUM(o.Profit) * 1.0 / NULLIF(SUM(o.Sales), 0), 4) AS GrossMarginPct,
    ROUND(AVG(o.Discount), 4) AS AvgDiscountRate,
    SUM(o.IsLossMaking) AS LossMakingOrdersCount,
    ROUND(SUM(o.IsLossMaking) * 100.0 / COUNT(*), 2) AS LossMakingRatePct,
    ROUND(SUM(CASE WHEN o.Profit < 0 THEN ABS(o.Profit) ELSE 0 END), 2) AS CashLeakageDollar
FROM fact_orders o
GROUP BY o.DiscountBracket
ORDER BY AvgDiscountRate ASC;
