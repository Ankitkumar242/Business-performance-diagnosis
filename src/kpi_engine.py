"""
KPI Engine Module
Business Performance Diagnosis & Decision Intelligence Platform

Computes core commercial, operational, and variance metrics in Python.
Uses exact formulas, decimal precision, and zero-denominator handling
consistent with the SQL Data Warehouse layer.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division preventing division-by-zero or NaN propagation."""
    if denominator is None or denominator == 0 or np.isnan(denominator) or np.isinf(denominator):
        return default
    if numerator is None or np.isnan(numerator) or np.isinf(numerator):
        return default
    return float(numerator / denominator)


def calculate_portfolio_kpis(df_orders: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes overall portfolio-level financial and operational KPIs.
    Handles empty DataFrames safely.
    """
    if df_orders is None or df_orders.empty:
        return {
            "TotalOrderLines": 0,
            "DistinctOrders": 0,
            "TotalRevenue": 0.0,
            "TotalCOGS": 0.0,
            "TotalProfit": 0.0,
            "GrossMarginPct": 0.0,
            "AvgOrderValue": 0.0,
            "TotalQuantity": 0,
            "LossMakingOrderLines": 0,
            "LossMakingSharePct": 0.0,
            "TotalCashLeakageDollar": 0.0,
            "ReturnedOrderLines": 0,
            "ReturnRatePct": 0.0,
            "AvgFulfillmentDays": 0.0,
        }

    total_revenue = round(float(df_orders["Sales"].sum()), 2)
    total_profit = round(float(df_orders["Profit"].sum()), 2)
    total_cogs = round(float(df_orders["COGS"].sum()), 2) if "COGS" in df_orders.columns else round(total_revenue - total_profit, 2)
    distinct_orders = int(df_orders["OrderID"].nunique()) if "OrderID" in df_orders.columns else len(df_orders)
    total_lines = len(df_orders)
    total_qty = int(df_orders["Quantity"].sum()) if "Quantity" in df_orders.columns else 0

    gross_margin_pct = round(safe_divide(total_profit, total_revenue, 0.0), 4)
    avg_order_value = round(safe_divide(total_revenue, distinct_orders, 0.0), 2)

    loss_mask = df_orders["Profit"] < 0
    loss_lines = int(loss_mask.sum())
    loss_share_pct = round(safe_divide(loss_lines * 100.0, total_lines, 0.0), 2)
    cash_leakage = round(float(df_orders.loc[loss_mask, "Profit"].abs().sum()), 2)

    returned_lines = int(df_orders["IsReturned"].sum()) if "IsReturned" in df_orders.columns else 0
    return_rate_pct = round(safe_divide(returned_lines * 100.0, total_lines, 0.0), 2)
    avg_fulfillment = round(float(df_orders["FulfillmentDays"].mean()), 2) if "FulfillmentDays" in df_orders.columns else 0.0

    return {
        "TotalOrderLines": total_lines,
        "DistinctOrders": distinct_orders,
        "TotalRevenue": total_revenue,
        "TotalCOGS": total_cogs,
        "TotalProfit": total_profit,
        "GrossMarginPct": gross_margin_pct,
        "AvgOrderValue": avg_order_value,
        "TotalQuantity": total_qty,
        "LossMakingOrderLines": loss_lines,
        "LossMakingSharePct": loss_share_pct,
        "TotalCashLeakageDollar": cash_leakage,
        "ReturnedOrderLines": returned_lines,
        "ReturnRatePct": return_rate_pct,
        "AvgFulfillmentDays": avg_fulfillment,
    }


def calculate_regional_kpis(df_orders: pd.DataFrame, df_geo: pd.DataFrame) -> pd.DataFrame:
    """Computes regional performance breakdown matching SQL view v_regional_performance."""
    if df_orders.empty or df_geo.empty:
        return pd.DataFrame()

    merged = df_orders.merge(df_geo, on="GeographyID")
    records = []
    for region, grp in merged.groupby("Region"):
        rev = round(float(grp["Sales"].sum()), 2)
        prof = round(float(grp["Profit"].sum()), 2)
        margin = round(safe_divide(prof, rev, 0.0), 4)
        avg_disc = round(float(grp["Discount"].mean()), 4)
        loss_lines = int((grp["Profit"] < 0).sum())
        loss_pct = round(safe_divide(loss_lines * 100.0, len(grp), 0.0), 2)
        leakage = round(float(grp.loc[grp["Profit"] < 0, "Profit"].abs().sum()), 2)
        ret_lines = int(grp["IsReturned"].sum())
        ret_pct = round(safe_divide(ret_lines * 100.0, len(grp), 0.0), 2)
        avg_days = round(float(grp["FulfillmentDays"].mean()), 2)

        records.append({
            "Region": region,
            "DistinctOrders": int(grp["OrderID"].nunique()),
            "DistinctCustomers": int(grp["CustomerID"].nunique()),
            "ActiveStates": int(grp["State"].nunique()),
            "ActiveCities": int(grp["City"].nunique()),
            "TotalRevenue": rev,
            "TotalProfit": prof,
            "GrossMarginPct": margin,
            "AvgDiscount": avg_disc,
            "LossMakingTransactions": loss_lines,
            "LossMakingSharePct": loss_pct,
            "CashLeakageDollar": leakage,
            "ReturnedOrderLines": ret_lines,
            "ReturnRatePct": ret_pct,
            "AvgFulfillmentDays": avg_days,
        })

    return pd.DataFrame(records).sort_values("TotalRevenue", ascending=False).reset_index(drop=True)


def calculate_subcategory_kpis(df_orders: pd.DataFrame, df_prod: pd.DataFrame) -> pd.DataFrame:
    """Computes subcategory profitability matching SQL view v_subcategory_profitability."""
    if df_orders.empty or df_prod.empty:
        return pd.DataFrame()

    merged = df_orders.merge(df_prod, on="ProductID")
    records = []
    for (category, subcat), grp in merged.groupby(["Category", "SubCategory"]):
        rev = round(float(grp["Sales"].sum()), 2)
        prof = round(float(grp["Profit"].sum()), 2)
        margin = round(safe_divide(prof, rev, 0.0), 4)
        avg_disc = round(float(grp["Discount"].mean()), 4)
        max_disc = round(float(grp["Discount"].max()), 4)
        loss_lines = int((grp["Profit"] < 0).sum())
        loss_pct = round(safe_divide(loss_lines * 100.0, len(grp), 0.0), 2)
        neg_prof = round(float(grp.loc[grp["Profit"] < 0, "Profit"].sum()), 2)

        tier = "Loss-Making Sub-Category" if prof < 0 else ("Low Margin (<10%)" if margin < 0.10 else "Healthy Margin (>=10%)")

        records.append({
            "Category": category,
            "SubCategory": subcat,
            "TotalOrderLines": len(grp),
            "TotalUnitsSold": int(grp["Quantity"].sum()),
            "TotalRevenue": rev,
            "TotalProfit": prof,
            "GrossMarginPct": margin,
            "AvgDiscountRate": avg_disc,
            "MaxDiscountGiven": max_disc,
            "LossMakingLines": loss_lines,
            "LossMakingLinePct": loss_pct,
            "NegativeProfitTally": neg_prof,
            "ProfitabilityTier": tier,
        })

    return pd.DataFrame(records).sort_values("TotalProfit", ascending=True).reset_index(drop=True)


def calculate_discount_bracket_kpis(df_orders: pd.DataFrame) -> pd.DataFrame:
    """Computes discount tier analysis matching SQL view v_discount_bracket_margin_leakage."""
    if df_orders.empty:
        return pd.DataFrame()

    records = []
    for bracket, grp in df_orders.groupby("DiscountBracket"):
        rev = round(float(grp["Sales"].sum()), 2)
        prof = round(float(grp["Profit"].sum()), 2)
        margin = round(safe_divide(prof, rev, 0.0), 4)
        avg_disc = round(float(grp["Discount"].mean()), 4)
        loss_lines = int((grp["Profit"] < 0).sum())
        loss_pct = round(safe_divide(loss_lines * 100.0, len(grp), 0.0), 2)
        leakage = round(float(grp.loc[grp["Profit"] < 0, "Profit"].abs().sum()), 2)

        records.append({
            "DiscountBracket": bracket,
            "TotalTransactions": len(grp),
            "TotalQuantity": int(grp["Quantity"].sum()),
            "TotalRevenue": rev,
            "TotalProfit": prof,
            "GrossMarginPct": margin,
            "AvgDiscountRate": avg_disc,
            "LossMakingOrdersCount": loss_lines,
            "LossMakingRatePct": loss_pct,
            "CashLeakageDollar": leakage,
        })

    return pd.DataFrame(records).sort_values("AvgDiscountRate", ascending=True).reset_index(drop=True)


if __name__ == "__main__":
    root = get_project_root()
    df_o = pd.read_csv(root / "data" / "processed" / "fact_orders.csv")
    df_g = pd.read_csv(root / "data" / "processed" / "dim_geography.csv")
    df_p = pd.read_csv(root / "data" / "processed" / "dim_product.csv")

    kpis = calculate_portfolio_kpis(df_o)
    print("=" * 70)
    print("KPI ENGINE VERIFICATION")
    print("=" * 70)
    for k, v in kpis.items():
        print(f"  {k:<28}: {v}")
