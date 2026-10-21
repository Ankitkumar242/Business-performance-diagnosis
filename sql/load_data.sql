-- ======================================================================
-- SQL SCRIPT: DIRECT CLI LOAD INSTRUCTIONS & QUERIES
-- Project: Business Performance Diagnosis & Decision Intelligence Platform
-- ======================================================================

-- PRAGMA Setting for Foreign Keys
PRAGMA foreign_keys = ON;

-- If using SQLite CLI directly (sqlite3.exe sql/business_bi.db):
-- .mode csv
-- .import --skip 1 data/processed/dim_ship_mode.csv dim_ship_mode
-- .import --skip 1 data/processed/dim_customer.csv dim_customer
-- .import --skip 1 data/processed/dim_product.csv dim_product
-- .import --skip 1 data/processed/dim_geography.csv dim_geography
-- .import --skip 1 data/processed/dim_date.csv dim_date
-- .import --skip 1 data/processed/fact_targets.csv fact_targets
-- .import --skip 1 data/processed/fact_orders.csv fact_orders

-- Quick verification query to verify row counts across all 7 tables:
SELECT 'dim_ship_mode' AS TableName, COUNT(*) AS RowCount FROM dim_ship_mode
UNION ALL
SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL
SELECT 'dim_geography', COUNT(*) FROM dim_geography
UNION ALL
SELECT 'dim_date', COUNT(*) FROM dim_date
UNION ALL
SELECT 'fact_targets', COUNT(*) FROM fact_targets
UNION ALL
SELECT 'fact_orders', COUNT(*) FROM fact_orders;
