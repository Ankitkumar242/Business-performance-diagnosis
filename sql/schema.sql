-- ======================================================================
-- DATABASE SCHEMA DDL: STAR SCHEMA RELATIONAL WAREHOUSE
-- Project: Business Performance Diagnosis & Decision Intelligence Platform
-- Target Database: SQLite 3 (sql/business_bi.db)
-- ======================================================================

PRAGMA foreign_keys = ON;

-- 1. DimDate (Calendar Dimension: 2015-01-01 to 2019-12-31)
CREATE TABLE IF NOT EXISTS dim_date (
    DateKey INTEGER PRIMARY KEY,
    FullDate TEXT NOT NULL UNIQUE,
    Year INTEGER NOT NULL CHECK(Year >= 2015),
    Quarter TEXT NOT NULL,
    QuarterNumber INTEGER NOT NULL CHECK(QuarterNumber BETWEEN 1 AND 4),
    YearQuarter TEXT NOT NULL,
    Month INTEGER NOT NULL CHECK(Month BETWEEN 1 AND 12),
    MonthName TEXT NOT NULL,
    MonthShort TEXT NOT NULL,
    YearMonth TEXT NOT NULL,
    DayOfMonth INTEGER NOT NULL CHECK(DayOfMonth BETWEEN 1 AND 31),
    DayOfWeek INTEGER NOT NULL CHECK(DayOfWeek BETWEEN 1 AND 7),
    DayName TEXT NOT NULL,
    IsWeekend INTEGER NOT NULL CHECK(IsWeekend IN (0, 1))
);

-- 2. DimCustomer (793 Unique Customers)
CREATE TABLE IF NOT EXISTS dim_customer (
    CustomerID TEXT PRIMARY KEY,
    CustomerName TEXT NOT NULL,
    Segment TEXT NOT NULL CHECK(Segment IN ('Consumer', 'Corporate', 'Home Office'))
);

-- 3. DimProduct (1,862 Unique Products)
CREATE TABLE IF NOT EXISTS dim_product (
    ProductID TEXT PRIMARY KEY,
    Category TEXT NOT NULL CHECK(Category IN ('Furniture', 'Office Supplies', 'Technology')),
    SubCategory TEXT NOT NULL,
    ProductName TEXT NOT NULL
);

-- 4. DimGeography (632 Unique Geographic Nodes)
CREATE TABLE IF NOT EXISTS dim_geography (
    GeographyID INTEGER PRIMARY KEY,
    City TEXT NOT NULL,
    State TEXT NOT NULL,
    PostalCode TEXT NOT NULL,
    Region TEXT NOT NULL CHECK(Region IN ('Central', 'East', 'South', 'West')),
    Country TEXT NOT NULL
);

-- 5. DimShipMode (4 Shipping Modes with SLA Standards)
CREATE TABLE IF NOT EXISTS dim_ship_mode (
    ShipModeID INTEGER PRIMARY KEY,
    ShipMode TEXT NOT NULL UNIQUE,
    StandardSLADays INTEGER NOT NULL CHECK(StandardSLADays >= 0)
);

-- 6. FactTargets (576 Monthly Targets: 48 Months x 4 Regions x 3 Categories)
-- GOVERNANCE NOTICE: Synthetic managerial budget quotas for variance modeling
CREATE TABLE IF NOT EXISTS fact_targets (
    TargetID INTEGER PRIMARY KEY,
    TargetDateKey INTEGER NOT NULL,
    Year INTEGER NOT NULL,
    Month INTEGER NOT NULL,
    YearMonth TEXT NOT NULL,
    Region TEXT NOT NULL CHECK(Region IN ('Central', 'East', 'South', 'West')),
    Category TEXT NOT NULL CHECK(Category IN ('Furniture', 'Office Supplies', 'Technology')),
    TargetRevenue REAL NOT NULL CHECK(TargetRevenue >= 0),
    TargetProfit REAL NOT NULL,
    TargetMarginPct REAL NOT NULL,
    TargetType TEXT NOT NULL,
    FOREIGN KEY (TargetDateKey) REFERENCES dim_date(DateKey) ON DELETE RESTRICT
);

-- 7. FactOrders (9,994 Transactional Order Line Items)
CREATE TABLE IF NOT EXISTS fact_orders (
    RowID INTEGER PRIMARY KEY,
    OrderID TEXT NOT NULL,
    OrderDateKey INTEGER NOT NULL,
    ShipDateKey INTEGER NOT NULL,
    CustomerID TEXT NOT NULL,
    ProductID TEXT NOT NULL,
    GeographyID INTEGER NOT NULL,
    ShipModeID INTEGER NOT NULL,
    Sales REAL NOT NULL CHECK(Sales >= 0),
    Quantity INTEGER NOT NULL CHECK(Quantity > 0),
    Discount REAL NOT NULL CHECK(Discount >= 0.0 AND Discount <= 1.0),
    Profit REAL NOT NULL,
    COGS REAL NOT NULL,
    ProfitMarginPct REAL NOT NULL,
    UnitPrice REAL NOT NULL CHECK(UnitPrice >= 0),
    FulfillmentDays INTEGER NOT NULL CHECK(FulfillmentDays >= 0),
    IsLossMaking INTEGER NOT NULL CHECK(IsLossMaking IN (0, 1)),
    IsReturned INTEGER NOT NULL CHECK(IsReturned IN (0, 1)),
    DiscountBracket TEXT NOT NULL,
    FOREIGN KEY (OrderDateKey) REFERENCES dim_date(DateKey) ON DELETE RESTRICT,
    FOREIGN KEY (ShipDateKey) REFERENCES dim_date(DateKey) ON DELETE RESTRICT,
    FOREIGN KEY (CustomerID) REFERENCES dim_customer(CustomerID) ON DELETE RESTRICT,
    FOREIGN KEY (ProductID) REFERENCES dim_product(ProductID) ON DELETE RESTRICT,
    FOREIGN KEY (GeographyID) REFERENCES dim_geography(GeographyID) ON DELETE RESTRICT,
    FOREIGN KEY (ShipModeID) REFERENCES dim_ship_mode(ShipModeID) ON DELETE RESTRICT
);

-- Indexes for Query Performance and Join Optimization
CREATE INDEX IF NOT EXISTS idx_orders_orderdate ON fact_orders(OrderDateKey);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON fact_orders(CustomerID);
CREATE INDEX IF NOT EXISTS idx_orders_product ON fact_orders(ProductID);
CREATE INDEX IF NOT EXISTS idx_orders_geography ON fact_orders(GeographyID);
CREATE INDEX IF NOT EXISTS idx_orders_shipmode ON fact_orders(ShipModeID);
CREATE INDEX IF NOT EXISTS idx_targets_date ON fact_targets(TargetDateKey);
CREATE INDEX IF NOT EXISTS idx_targets_reg_cat ON fact_targets(Region, Category);
