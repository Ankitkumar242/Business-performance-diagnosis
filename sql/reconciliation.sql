-- ======================================================================
-- SQL RECONCILIATION BENCHMARK QUERIES
-- Project: Business Performance Diagnosis & Decision Intelligence Platform
-- Target Database: SQLite 3 (sql/business_bi.db)
-- ======================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------
-- RECONCILIATION 1: Portfolio Grand Totals
-- ----------------------------------------------------------------------
SELECT
    'PORTFOLIO_GRAND_TOTALS' AS BenchmarkName,
    COUNT(*) AS TotalOrderLines,
    COUNT(DISTINCT OrderID) AS DistinctOrders,
    ROUND(SUM(Sales), 2) AS TotalRevenue,
    ROUND(SUM(COGS), 2) AS TotalCOGS,
    ROUND(SUM(Profit), 2) AS TotalProfit,
    ROUND(SUM(Profit) * 1.0 / NULLIF(SUM(Sales), 0), 4) AS GrossMarginPct,
    SUM(Quantity) AS TotalQuantity,
    SUM(IsLossMaking) AS LossMakingCount,
    ROUND(SUM(CASE WHEN Profit < 0 THEN ABS(Profit) ELSE 0 END), 2) AS TotalCashLeakage
FROM fact_orders;

-- ----------------------------------------------------------------------
-- RECONCILIATION 2: Regional Revenue & Profit Breakdown
-- ----------------------------------------------------------------------
SELECT
    g.Region,
    COUNT(*) AS OrderLineCount,
    ROUND(SUM(o.Sales), 2) AS RegionalRevenue,
    ROUND(SUM(o.Profit), 2) AS RegionalProfit,
    ROUND(SUM(o.Profit) * 1.0 / NULLIF(SUM(o.Sales), 0), 4) AS RegionalMarginPct,
    SUM(o.Quantity) AS UnitsSold
FROM fact_orders o
JOIN dim_geography g ON o.GeographyID = g.GeographyID
GROUP BY g.Region
ORDER BY g.Region;

-- ----------------------------------------------------------------------
-- RECONCILIATION 3: Product Category Breakdown
-- ----------------------------------------------------------------------
SELECT
    p.Category,
    COUNT(*) AS OrderLineCount,
    ROUND(SUM(o.Sales), 2) AS CategoryRevenue,
    ROUND(SUM(o.Profit), 2) AS CategoryProfit,
    ROUND(SUM(o.Profit) * 1.0 / NULLIF(SUM(o.Sales), 0), 4) AS CategoryMarginPct,
    SUM(o.Quantity) AS UnitsSold
FROM fact_orders o
JOIN dim_product p ON o.ProductID = p.ProductID
GROUP BY p.Category
ORDER BY p.Category;

-- ----------------------------------------------------------------------
-- RECONCILIATION 4: Target Totals Verification
-- ----------------------------------------------------------------------
SELECT
    'FACT_TARGETS_TOTALS' AS BenchmarkName,
    COUNT(*) AS TotalTargetRows,
    ROUND(SUM(TargetRevenue), 2) AS TotalTargetRevenue,
    ROUND(SUM(TargetProfit), 2) AS TotalTargetProfit,
    ROUND(SUM(TargetProfit) * 1.0 / NULLIF(SUM(TargetRevenue), 0), 4) AS BlendedTargetMarginPct
FROM fact_targets;
