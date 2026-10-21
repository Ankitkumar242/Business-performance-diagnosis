"""
Diagnostic Reporting & Chart Generation Module
Business Performance Diagnosis & Decision Intelligence Platform

Generates 4 high-resolution diagnostic visualizations saved to reports/figures/:
1. pareto_revenue_by_subcategory.png
2. profit_margin_vs_discount_scatter.png
3. regional_target_attainment_waterfall.png
4. fulfillment_sla_adherence_breakdown.png

Each chart includes clear annotations, accessible styling, and documented business meaning.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def set_corporate_style():
    """Sets clean corporate chart aesthetics."""
    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8


def generate_pareto_chart(df_orders: pd.DataFrame, df_prod: pd.DataFrame, out_path: Path):
    """
    Chart 1: Pareto Curve (Sub-Category Revenue & Cumulative Share)
    Business Meaning: 80/20 rule analysis showing which product lines drive 80% of sales.
    """
    merged = df_orders.merge(df_prod[["ProductID", "SubCategory"]], on="ProductID")
    subcat_rev = merged.groupby("SubCategory")["Sales"].sum().sort_values(ascending=False).reset_index()
    total_rev = subcat_rev["Sales"].sum()
    subcat_rev["CumulativePct"] = (subcat_rev["Sales"].cumsum() / total_rev) * 100.0

    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)

    # Primary axis: Bars for revenue
    bars = ax1.bar(
        subcat_rev["SubCategory"],
        subcat_rev["Sales"] / 1000.0,
        color="#1f77b4",
        edgecolor="#0f4c81",
        alpha=0.85,
        width=0.6,
        label="Revenue ($K)"
    )
    ax1.set_ylabel("Total Revenue ($ Thousands)", color="#0f4c81", fontsize=11, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor="#0f4c81")
    ax1.set_xticks(range(len(subcat_rev)))
    ax1.set_xticklabels(subcat_rev["SubCategory"], rotation=45, ha="right", fontsize=9)
    ax1.set_ylim(0, (subcat_rev["Sales"].max() / 1000.0) * 1.15)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"${x:,.0f}K"))

    # Secondary axis: Line for cumulative percentage
    ax2 = ax1.twinx()
    line = ax2.plot(
        subcat_rev["SubCategory"],
        subcat_rev["CumulativePct"],
        color="#d62728",
        marker="o",
        linewidth=2.2,
        markersize=5,
        label="Cumulative Share (%)"
    )
    ax2.set_ylabel("Cumulative Share (%)", color="#d62728", fontsize=11, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor="#d62728")
    ax2.set_ylim(0, 105)
    ax2.yaxis.set_major_formatter(ticker.PercentFormatter())
    ax2.grid(False)

    # 80% Benchmark Line
    ax2.axhline(80, color="#2ca02c", linestyle="--", linewidth=1.5, alpha=0.9, label="80% Pareto Cutoff")
    ax2.text(
        0, 81.5, "80% Revenue Threshold",
        color="#2ca02c", fontweight="bold", fontsize=9
    )

    plt.title("Product Sub-Category Pareto Analysis: Revenue Concentration & Cumulative Share", fontsize=13, fontweight="bold", pad=15)
    fig.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[CHART 1] Pareto Curve saved to: {out_path.name}")


def generate_margin_vs_discount_scatter(df_orders: pd.DataFrame, out_path: Path):
    """
    Chart 2: Profit Margin % vs. Discount Depth Scatter Plot
    Business Meaning: Demonstrates margin destruction when discount rates exceed 20%.
    """
    # Sample 2,000 points if dataset is large to maintain crisp visual density without overplotting
    sample_df = df_orders.sample(n=min(3000, len(df_orders)), random_state=42)

    palette = {
        "0% (No Discount)": "#2ca02c",
        "1-10% (Low)": "#1f77b4",
        "11-20% (Moderate)": "#ff7f0e",
        "21-40% (High)": "#e377c2",
        ">40% (Severe)": "#d62728"
    }

    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)

    # Plot points by discount tier
    for bracket, color in palette.items():
        subset = sample_df[sample_df["DiscountBracket"] == bracket]
        ax.scatter(
            subset["Discount"] * 100.0,
            subset["ProfitMarginPct"] * 100.0,
            color=color,
            alpha=0.45,
            edgecolors="none",
            s=22,
            label=bracket
        )

    # Zero Margin Threshold Line
    ax.axhline(0, color="#333333", linestyle="-", linewidth=1.2, label="Zero Margin (Break-even)")
    ax.axvline(20, color="#d62728", linestyle=":", linewidth=1.4, label="20% Discount Danger Zone")

    ax.set_xlabel("Discount Rate (%)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Profit Margin (%)", fontsize=11, fontweight="bold")
    ax.set_ylim(-150, 60)
    ax.set_xlim(-2, 85)

    ax.xaxis.set_major_formatter(ticker.PercentFormatter())
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())

    # Annotate the Danger Zone
    ax.annotate(
        "Margin Collapse Zone\n(Discounts > 20% heavily loss-making)",
        xy=(40, -50), xytext=(45, -110),
        arrowprops=dict(facecolor="#d62728", shrink=0.05, width=1.2, headwidth=6),
        fontsize=9, fontweight="bold", color="#d62728",
        bbox=dict(boxstyle="round,pad=0.4", fc="#fff1f0", ec="#d62728", lw=0.8)
    )

    plt.title("Profit Margin % vs. Discount Rate: Identification of the 20% Erosion Threshold", fontsize=13, fontweight="bold", pad=15)
    plt.legend(loc="upper right", frameon=True, fontsize=8.5, title="Discount Tier")
    fig.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[CHART 2] Margin vs Discount Scatter saved to: {out_path.name}")


def generate_waterfall_chart(df_orders: pd.DataFrame, df_targets: pd.DataFrame, df_geo: pd.DataFrame, out_path: Path):
    """
    Chart 3: Regional Target Attainment & Variance Breakdown (Waterfall-Style Bar)
    Business Meaning: Shows Target Revenue baseline, regional shortfalls, and final Actual Revenue.
    """
    merged = df_orders.merge(df_geo[["GeographyID", "Region"]], on="GeographyID")
    actual_by_reg = merged.groupby("Region")["Sales"].sum()
    target_by_reg = df_targets.groupby("Region")["TargetRevenue"].sum()

    total_target = df_targets["TargetRevenue"].sum()
    total_actual = df_orders["Sales"].sum()

    regions = ["Central", "East", "South", "West"]
    variances = [actual_by_reg[r] - target_by_reg[r] for r in regions]

    # Categories for waterfall: Target, 4 regional variances, Actual
    categories = ["Budget Target"] + [f"{r} Variance" for r in regions] + ["Actual Revenue"]
    values = [total_target / 1000.0] + [v / 1000.0 for v in variances] + [total_actual / 1000.0]

    colors = ["#3366cc"] + ["#2ca02c" if v >= 0 else "#d62728" for v in variances] + ["#109618"]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    bars = ax.bar(categories, values, color=colors, edgecolor="#333333", alpha=0.85, width=0.55)

    ax.set_ylabel("Revenue ($ Thousands)", fontsize=11, fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"${x:,.0f}K"))
    ax.axhline(0, color="#666666", linewidth=0.8)

    # Add data labels
    for bar in bars:
        h = bar.get_height()
        va = "bottom" if h >= 0 else "top"
        y_pos = h + (15 if h >= 0 else -35)
        ax.text(
            bar.get_x() + bar.get_width() / 2.0, y_pos,
            f"${h:,.1f}K",
            ha="center", va=va, fontsize=8.5, fontweight="bold"
        )

    plt.title("Executive Revenue Variance Bridge: Budget Target to Actual Revenue", fontsize=13, fontweight="bold", pad=15)
    plt.xticks(rotation=20, ha="right", fontsize=9.5)
    ax.set_ylim(-150, max(values) * 1.18)
    fig.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[CHART 3] Regional Variance Waterfall saved to: {out_path.name}")


def generate_fulfillment_sla_chart(df_orders: pd.DataFrame, df_ship: pd.DataFrame, out_path: Path):
    """
    Chart 4: Carrier SLA Adherence & Average Fulfillment Days by Ship Mode
    Business Meaning: Logistics operational diagnostic measuring carrier lead times against SLAs.
    """
    merged = df_orders.merge(df_ship, on="ShipModeID")
    sla_stats = []
    for mode, grp in merged.groupby("ShipMode"):
        sla_days = grp["StandardSLADays"].iloc[0]
        on_time = (grp["FulfillmentDays"] <= sla_days).sum()
        adherence_pct = (on_time / len(grp)) * 100.0
        avg_days = grp["FulfillmentDays"].mean()

        sla_stats.append({
            "ShipMode": mode,
            "CarrierSLADays": sla_days,
            "ActualAvgDays": avg_days,
            "SLAAdherencePct": adherence_pct,
            "OrderCount": len(grp)
        })

    sla_df = pd.DataFrame(sla_stats).sort_values("CarrierSLADays", ascending=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    # Panel 1: SLA Adherence %
    bar_colors = ["#2ca02c" if p >= 90 else "#ff7f0e" if p >= 75 else "#d62728" for p in sla_df["SLAAdherencePct"]]
    bars1 = ax1.bar(sla_df["ShipMode"], sla_df["SLAAdherencePct"], color=bar_colors, width=0.55, edgecolor="#333333")
    ax1.set_ylabel("SLA Compliance Rate (%)", fontsize=10.5, fontweight="bold")
    ax1.set_ylim(0, 115)
    ax1.yaxis.set_major_formatter(ticker.PercentFormatter())
    ax1.axhline(95, color="#2ca02c", linestyle="--", linewidth=1.2, label="95% Target SLA")
    ax1.set_title("Carrier SLA Adherence Rate (%)", fontsize=11.5, fontweight="bold")
    ax1.tick_params(axis="x", rotation=20)
    ax1.legend(loc="upper right", fontsize=8.5)

    for b in bars1:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width() / 2.0, h + 2, f"{h:.1f}%", ha="center", fontsize=8.5, fontweight="bold")

    # Panel 2: Actual vs Standard SLA Days
    x = np.arange(len(sla_df))
    width = 0.35
    ax2.bar(x - width/2, sla_df["CarrierSLADays"], width, label="Standard Carrier SLA (Days)", color="#4682b4", edgecolor="#333333")
    ax2.bar(x + width/2, sla_df["ActualAvgDays"], width, label="Actual Avg Fulfillment (Days)", color="#ffbb78", edgecolor="#333333")
    ax2.set_ylabel("Fulfillment Cycle (Days)", fontsize=10.5, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(sla_df["ShipMode"], rotation=20)
    ax2.set_title("Standard SLA vs. Actual Delivery Lead Time", fontsize=11.5, fontweight="bold")
    ax2.set_ylim(0, 8)
    ax2.legend(loc="upper left", fontsize=8.5)

    fig.suptitle("Supply Chain Operational Diagnostic: Shipping Lead Times & SLA Compliance", fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[CHART 4] Fulfillment SLA Chart saved to: {out_path.name}")


def generate_all_diagnostic_reports():
    """Generates all 4 high-resolution diagnostic charts and writes to reports/figures/."""
    root = get_project_root()
    fig_dir = root / "reports" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    set_corporate_style()

    df_o = pd.read_csv(root / "data" / "processed" / "fact_orders.csv")
    df_t = pd.read_csv(root / "data" / "processed" / "fact_targets.csv")
    df_p = pd.read_csv(root / "data" / "processed" / "dim_product.csv")
    df_g = pd.read_csv(root / "data" / "processed" / "dim_geography.csv")
    df_s = pd.read_csv(root / "data" / "processed" / "dim_ship_mode.csv")

    print("=" * 70)
    print("STAGE 6: GENERATING HIGH-RESOLUTION DIAGNOSTIC CHARTS")
    print("=" * 70)
    generate_pareto_chart(df_o, df_p, fig_dir / "pareto_revenue_by_subcategory.png")
    generate_margin_vs_discount_scatter(df_o, fig_dir / "profit_margin_vs_discount_scatter.png")
    generate_waterfall_chart(df_o, df_t, df_g, fig_dir / "regional_target_attainment_waterfall.png")
    generate_fulfillment_sla_chart(df_o, df_s, fig_dir / "fulfillment_sla_adherence_breakdown.png")
    print("=" * 70)
    print("ALL 4 DIAGNOSTIC CHARTS GENERATED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    generate_all_diagnostic_reports()
