"""
E-commerce Sales Analyzer
=========================
NumPy + Pandas + Matplotlib + Seaborn se e-commerce sales ka poora analysis:

    1. Overall sales & profit summary
    2. Best-selling products (units + revenue + profit)
    3. Monthly revenue trend
    4. Customer spending & segmentation
    5. Regional performance

Usage:
    python ecommerce_sales_analyzer.py                      # sample data ke saath demo
    python ecommerce_sales_analyzer.py --data my_sales.csv  # apni CSV ke saath
    python ecommerce_sales_analyzer.py --rows 20000 --seed 7

Apni CSV me ye columns hone chahiye:
    order_id, order_date, customer_id, product, category,
    region, quantity, unit_price, cost_price, discount
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # GUI ke bina bhi charts save ho jayein
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

REQUIRED_COLUMNS = [
    "order_id", "order_date", "customer_id", "product", "category",
    "region", "quantity", "unit_price", "cost_price", "discount",
]

sns.set_theme(style="whitegrid", context="notebook", palette="viridis")
plt.rcParams.update({"figure.dpi": 110, "axes.titleweight": "bold", "axes.titlesize": 13})


# --------------------------------------------------------------------------- #
# 1. Data: sample banana / load karna / saaf karna
# --------------------------------------------------------------------------- #
def generate_sample_data(n_rows: int = 8000, seed: int = 42) -> pd.DataFrame:
    """Realistic-sa dikhne wala fake e-commerce data banata hai (demo ke liye)."""
    rng = np.random.default_rng(seed)

    # product: (category, selling price, cost price)
    catalog = {
        "Wireless Earbuds":   ("Electronics", 2499, 1500),
        "Smart Watch":        ("Electronics", 4999, 3300),
        "Power Bank":         ("Electronics", 1299, 800),
        "Bluetooth Speaker":  ("Electronics", 1999, 1250),
        "Running Shoes":      ("Fashion", 2999, 1700),
        "Denim Jacket":       ("Fashion", 2499, 1300),
        "Cotton T-Shirt":     ("Fashion", 599, 250),
        "Backpack":           ("Fashion", 1499, 750),
        "Air Fryer":          ("Home & Kitchen", 5499, 3800),
        "Mixer Grinder":      ("Home & Kitchen", 3299, 2200),
        "Cookware Set":       ("Home & Kitchen", 2799, 1700),
        "Yoga Mat":           ("Sports & Fitness", 899, 400),
        "Dumbbell Set":       ("Sports & Fitness", 2199, 1400),
        "Protein Powder":     ("Sports & Fitness", 2599, 1800),
        "Self-Help Book":     ("Books", 399, 180),
        "Notebook Pack":      ("Books", 249, 100),
    }
    products = list(catalog)
    # sasti cheezein zyada bikti hain
    popularity = np.array([1 / np.sqrt(catalog[p][1]) for p in products])
    popularity /= popularity.sum()

    regions = ["North", "South", "East", "West", "Central"]
    region_weights = [0.24, 0.28, 0.14, 0.26, 0.08]

    # Oct-Dec (festive season) me zyada orders
    month_weights = np.array([6, 6, 7, 7, 8, 7, 7, 8, 9, 12, 14, 13], dtype=float)
    month_weights /= month_weights.sum()

    months = rng.choice(np.arange(1, 13), size=n_rows, p=month_weights)
    days = rng.integers(1, 28, size=n_rows)
    dates = pd.to_datetime({"year": 2025, "month": months, "day": days})

    chosen = rng.choice(products, size=n_rows, p=popularity)
    unit_price = np.array([catalog[p][1] for p in chosen], dtype=float)
    cost_price = np.array([catalog[p][2] for p in chosen], dtype=float)

    # thoda price/cost variation, taaki data real lage
    unit_price = np.round(unit_price * rng.normal(1.0, 0.03, n_rows), 2)
    cost_price = np.round(cost_price * rng.normal(1.0, 0.02, n_rows), 2)

    # kuch customers baar-baar kharidte hain (loyal), baaki kabhi-kabhi
    n_customers = 900
    customer_pool = np.array([f"C{i:04d}" for i in range(1, n_customers + 1)])
    customer_weights = rng.pareto(2.0, n_customers) + 1
    customer_weights /= customer_weights.sum()

    df = pd.DataFrame({
        "order_id": [f"ORD{100000 + i}" for i in range(n_rows)],
        "order_date": dates,
        "customer_id": rng.choice(customer_pool, size=n_rows, p=customer_weights),
        "product": chosen,
        "category": [catalog[p][0] for p in chosen],
        "region": rng.choice(regions, size=n_rows, p=region_weights),
        "quantity": rng.poisson(1.0, n_rows) + 1,
        "unit_price": unit_price,
        "cost_price": cost_price,
        "discount": rng.choice([0.0, 0.05, 0.10, 0.20], size=n_rows, p=[0.5, 0.2, 0.2, 0.1]),
    })
    return df.sort_values("order_date").reset_index(drop=True)


def load_data(path: str | None, rows: int, seed: int) -> pd.DataFrame:
    """CSV load karta hai; path nahi diya to sample data banata hai."""
    if path is None:
        print(f"[info] CSV nahi mili, {rows} rows ka sample data bana raha hu (seed={seed})")
        return generate_sample_data(rows, seed)

    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"File nahi mili: {csv_path}")
    print(f"[info] Data load ho raha hai: {csv_path}")
    return pd.read_csv(csv_path)


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Data saaf karke revenue, cost, profit jaise naye columns jodta hai."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"In columns ki kami hai: {missing}")

    df = df[REQUIRED_COLUMNS].copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    before = len(df)
    df = df.drop_duplicates(subset="order_id").dropna()
    df = df[(df["quantity"] > 0) & (df["unit_price"] > 0)]
    df["discount"] = df["discount"].clip(0, 1)
    print(f"[info] Cleaning: {before - len(df)} kharab/duplicate rows hata di, {len(df)} bachi")

    df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount"])
    df["cost"] = df["quantity"] * df["cost_price"]
    df["profit"] = df["revenue"] - df["cost"]
    df["margin_pct"] = np.where(df["revenue"] > 0, df["profit"] / df["revenue"] * 100, 0)
    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    return df.reset_index(drop=True)


# --------------------------------------------------------------------------- #
# 2. Analysis functions
# --------------------------------------------------------------------------- #
def overall_summary(df: pd.DataFrame) -> dict:
    """Poore business ke headline numbers."""
    total_revenue = df["revenue"].sum()
    total_profit = df["profit"].sum()
    return {
        "Total Orders": df["order_id"].nunique(),
        "Unique Customers": df["customer_id"].nunique(),
        "Units Sold": int(df["quantity"].sum()),
        "Total Revenue": total_revenue,
        "Total Profit": total_profit,
        "Profit Margin %": total_profit / total_revenue * 100,
        "Avg Order Value": total_revenue / df["order_id"].nunique(),
        "Date Range": f"{df['order_date'].min():%d %b %Y} - {df['order_date'].max():%d %b %Y}",
    }


def product_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Har product ki units, revenue, profit aur margin."""
    out = (
        df.groupby(["product", "category"])
        .agg(units_sold=("quantity", "sum"), revenue=("revenue", "sum"), profit=("profit", "sum"))
        .reset_index()
    )
    out["margin_pct"] = out["profit"] / out["revenue"] * 100
    return out.sort_values("units_sold", ascending=False).reset_index(drop=True)


def category_performance(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("category").agg(revenue=("revenue", "sum"), profit=("profit", "sum")).reset_index()
    out["margin_pct"] = out["profit"] / out["revenue"] * 100
    return out.sort_values("profit", ascending=False).reset_index(drop=True)


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Mahine-wise revenue, profit, orders + month-over-month growth."""
    out = (
        df.groupby("month")
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
        .reset_index()
    )
    out["mom_growth_pct"] = out["revenue"].pct_change() * 100
    return out


def customer_spending(df: pd.DataFrame) -> pd.DataFrame:
    """Har customer ka total kharcha, orders, aur segment (Bronze -> Platinum)."""
    out = (
        df.groupby("customer_id")
        .agg(
            total_spent=("revenue", "sum"),
            orders=("order_id", "nunique"),
            units=("quantity", "sum"),
            last_purchase=("order_date", "max"),
        )
        .reset_index()
    )
    out["avg_order_value"] = out["total_spent"] / out["orders"]
    # rank se qcut karte hain taaki duplicate values pe error na aaye
    out["segment"] = pd.qcut(
        out["total_spent"].rank(method="first"),
        q=4,
        labels=["Bronze", "Silver", "Gold", "Platinum"],
    )
    return out.sort_values("total_spent", ascending=False).reset_index(drop=True)


def regional_performance(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby("region")
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
        )
        .reset_index()
    )
    out["margin_pct"] = out["profit"] / out["revenue"] * 100
    out["revenue_share_pct"] = out["revenue"] / out["revenue"].sum() * 100
    return out.sort_values("revenue", ascending=False).reset_index(drop=True)


# --------------------------------------------------------------------------- #
# 3. Charts
# --------------------------------------------------------------------------- #
def _money_axis(ax, axis: str = "y") -> None:
    """Axis ko Lakh / Crore me dikhata hai (Indian style)."""
    def fmt(x, _):
        if abs(x) >= 1e7:
            return f"{x / 1e7:.1f} Cr"
        if abs(x) >= 1e5:
            return f"{x / 1e5:.1f} L"
        if abs(x) >= 1e3:
            return f"{x / 1e3:.0f}K"
        return f"{x:.0f}"

    formatter = plt.FuncFormatter(fmt)
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(formatter)


def _save(fig, out_dir: Path, name: str) -> None:
    fig.tight_layout()
    fig.savefig(out_dir / name, bbox_inches="tight")
    plt.close(fig)
    print(f"   saved -> {out_dir / name}")


def plot_monthly_revenue(monthly: pd.DataFrame, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    labels = monthly["month"].dt.strftime("%b %y")
    ax.bar(labels, monthly["revenue"], color="#4c78a8", alpha=0.85, label="Revenue")
    ax.plot(labels, monthly["profit"], color="#f58518", marker="o", linewidth=2.5, label="Profit")

    peak = monthly["revenue"].idxmax()
    peak_value = monthly.loc[peak, "revenue"]
    ax.set_ylim(0, peak_value * 1.18)  # annotation ke liye jagah
    ax.annotate(
        "Peak month",
        xy=(peak, peak_value),
        xytext=(peak, peak_value * 1.09),
        ha="center", color="#c0392b", fontweight="bold",
        arrowprops={"arrowstyle": "->", "color": "#c0392b"},
    )
    ax.set_title("Monthly Revenue vs Profit")
    ax.set_xlabel("")
    ax.set_ylabel("Amount (Rs)")
    _money_axis(ax)
    ax.legend()
    _save(fig, out_dir, "01_monthly_revenue.png")


def plot_top_products(products: pd.DataFrame, out_dir: Path, top_n: int = 10) -> None:
    top = products.head(top_n)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    sns.barplot(data=top, y="product", x="units_sold", hue="product",
                palette="Blues_r", legend=False, ax=axes[0])
    axes[0].set_title(f"Top {top_n} Best-Selling Products (Units)")
    axes[0].set_xlabel("Units sold")
    axes[0].set_ylabel("")

    by_profit = products.sort_values("profit", ascending=False).head(top_n)
    sns.barplot(data=by_profit, y="product", x="profit", hue="product",
                palette="Greens_r", legend=False, ax=axes[1])
    axes[1].set_title(f"Top {top_n} Most Profitable Products")
    axes[1].set_xlabel("Total profit (Rs)")
    axes[1].set_ylabel("")
    _money_axis(axes[1], "x")
    _save(fig, out_dir, "02_top_products.png")


def plot_category_performance(categories: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].pie(
        categories["revenue"], labels=categories["category"], autopct="%1.1f%%",
        startangle=90, colors=sns.color_palette("Set2"), wedgeprops={"edgecolor": "white"},
    )
    axes[0].set_title("Revenue Share by Category")

    sns.barplot(data=categories, x="category", y="margin_pct", hue="category",
                palette="Set2", legend=False, ax=axes[1])
    axes[1].set_title("Profit Margin % by Category")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Margin %")
    axes[1].tick_params(axis="x", rotation=20)
    for container in axes[1].containers:
        axes[1].bar_label(container, fmt="%.1f%%", padding=3)
    _save(fig, out_dir, "03_category_performance.png")


def plot_customer_spending(customers: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    sns.histplot(customers["total_spent"], bins=40, kde=True, color="#7b5ea7", ax=axes[0])
    axes[0].axvline(customers["total_spent"].median(), color="red", linestyle="--",
                    label=f"Median: Rs {customers['total_spent'].median():,.0f}")
    axes[0].set_title("Customer Spending Distribution")
    axes[0].set_xlabel("Total spent (Rs)")
    axes[0].legend()

    seg = customers.groupby("segment", observed=True)["total_spent"].sum().reset_index()
    sns.barplot(data=seg, x="segment", y="total_spent", hue="segment",
                palette="YlOrBr", legend=False, ax=axes[1])
    axes[1].set_title("Revenue by Customer Segment")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Revenue (Rs)")
    _money_axis(axes[1])
    _save(fig, out_dir, "04_customer_spending.png")


def plot_regional_performance(df: pd.DataFrame, regions: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), gridspec_kw={"width_ratios": [1, 1.4]})

    melted = regions.melt(id_vars="region", value_vars=["revenue", "profit"],
                          var_name="metric", value_name="amount")
    sns.barplot(data=melted, x="region", y="amount", hue="metric",
                palette=["#4c78a8", "#54a24b"], ax=axes[0])
    axes[0].set_title("Revenue & Profit by Region")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Amount (Rs)")
    _money_axis(axes[0])

    pivot = df.pivot_table(index="region", columns=df["month"].dt.strftime("%b"),
                           values="revenue", aggfunc="sum")
    month_order = [m for m in pd.date_range("2000-01-01", periods=12, freq="MS").strftime("%b")
                   if m in pivot.columns]
    sns.heatmap(pivot[month_order] / 1e5, annot=True, fmt=".1f", cmap="YlGnBu",
                cbar_kws={"label": "Revenue (Lakh Rs)"}, ax=axes[1])
    axes[1].set_title("Region x Month Revenue Heatmap")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("")
    _save(fig, out_dir, "05_regional_performance.png")


def plot_correlation(df: pd.DataFrame, out_dir: Path) -> None:
    cols = ["quantity", "unit_price", "discount", "revenue", "profit", "margin_pct"]
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(df[cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Heatmap")
    _save(fig, out_dir, "06_correlation.png")


# --------------------------------------------------------------------------- #
# 4. Report
# --------------------------------------------------------------------------- #
def build_text_report(summary, products, categories, monthly, customers, regions) -> str:
    best_month = monthly.loc[monthly["revenue"].idxmax()]
    worst_month = monthly.loc[monthly["revenue"].idxmin()]
    top_region = regions.iloc[0]
    top5_share = customers.head(max(1, int(len(customers) * 0.05)))["total_spent"].sum() \
        / customers["total_spent"].sum() * 100

    lines = ["=" * 62, "   E-COMMERCE SALES ANALYSIS REPORT", "=" * 62, "", "-- OVERVIEW --"]
    for key, val in summary.items():
        if key in ("Total Revenue", "Total Profit", "Avg Order Value"):
            lines.append(f"{key:<20}: Rs {val:,.0f}")
        elif key == "Profit Margin %":
            lines.append(f"{key:<20}: {val:.1f}%")
        elif isinstance(val, (int, np.integer)):
            lines.append(f"{key:<20}: {val:,}")
        else:
            lines.append(f"{key:<20}: {val}")

    lines += ["", "-- KEY INSIGHTS --",
              f"* Best seller (units)  : {products.iloc[0]['product']} ({products.iloc[0]['units_sold']:,} units)",
              f"* Most profitable      : {products.sort_values('profit', ascending=False).iloc[0]['product']}",
              f"* Best category margin : {categories.sort_values('margin_pct', ascending=False).iloc[0]['category']}",
              f"* Peak month           : {best_month['month']:%B %Y} (Rs {best_month['revenue']:,.0f})",
              f"* Slowest month        : {worst_month['month']:%B %Y} (Rs {worst_month['revenue']:,.0f})",
              f"* Top region           : {top_region['region']} ({top_region['revenue_share_pct']:.1f}% of revenue)",
              f"* Top 5% customers     : {top5_share:.1f}% of total revenue",
              "", "-- TOP 5 PRODUCTS (by units) --",
              products.head(5)[["product", "units_sold", "revenue", "profit"]].round(0).to_string(index=False),
              "", "-- REGIONAL PERFORMANCE --",
              regions[["region", "revenue", "profit", "margin_pct"]].round(1).to_string(index=False),
              "", "-- TOP 5 CUSTOMERS --",
              customers.head(5)[["customer_id", "total_spent", "orders"]].round(0).to_string(index=False),
              ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# 5. Main
# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(description="E-commerce Sales Analyzer")
    parser.add_argument("--data", help="CSV file ka path (nahi diya to sample data banega)")
    parser.add_argument("--output", default="output", help="Charts/reports ka folder (default: output)")
    parser.add_argument("--rows", type=int, default=8000, help="Sample data me kitni rows")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (same result ke liye)")
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = load_data(args.data, args.rows, args.seed)
    if args.data is None:
        raw.to_csv(out_dir / "sample_sales_data.csv", index=False)

    df = prepare_data(raw)

    summary = overall_summary(df)
    products = product_performance(df)
    categories = category_performance(df)
    monthly = monthly_trend(df)
    customers = customer_spending(df)
    regions = regional_performance(df)

    print("\n[info] Charts ban rahe hain...")
    plot_monthly_revenue(monthly, out_dir)
    plot_top_products(products, out_dir)
    plot_category_performance(categories, out_dir)
    plot_customer_spending(customers, out_dir)
    plot_regional_performance(df, regions, out_dir)
    plot_correlation(df, out_dir)

    products.to_csv(out_dir / "product_performance.csv", index=False)
    monthly.to_csv(out_dir / "monthly_trend.csv", index=False)
    customers.to_csv(out_dir / "customer_spending.csv", index=False)
    regions.to_csv(out_dir / "regional_performance.csv", index=False)

    report = build_text_report(summary, products, categories, monthly, customers, regions)
    (out_dir / "sales_report.txt").write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"[done] Sab kuch '{out_dir}/' folder me save ho gaya.")


if __name__ == "__main__":
    main()
