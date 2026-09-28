"""
Report Generator Module
========================
Generates automated reports with visual summaries,
charts, and comprehensive data analysis outputs.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import json
from datetime import datetime


# ─────────────────────────────────────────────
# STYLE CONFIGURATION
# ─────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0f0f1a",
    "axes.facecolor": "#1a1a2e",
    "axes.edgecolor": "#2d2d4a",
    "axes.labelcolor": "#e0e0ff",
    "text.color": "#e0e0ff",
    "xtick.color": "#a0a0cc",
    "ytick.color": "#a0a0cc",
    "grid.color": "#2d2d4a",
    "grid.alpha": 0.5,
    "font.family": "sans-serif",
    "font.size": 11,
})

# Color palettes
GRADIENT_COLORS = ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#7c3aed"]
CATEGORY_COLORS = {
    "Electronics": "#6366f1",
    "Furniture": "#f59e0b",
    "Clothing": "#10b981",
    "Other": "#ef4444"
}
STATUS_COLORS = {
    "Completed": "#10b981",
    "Pending": "#f59e0b",
    "Cancelled": "#ef4444"
}


class ReportGenerator:
    """Generate comprehensive automated reports with visualizations."""

    def __init__(self, cleaned_data_path, output_dir="output/reports"):
        self.df = pd.read_csv(cleaned_data_path)
        self.output_dir = output_dir
        self.charts_dir = os.path.join(output_dir, "charts")
        self.report_data = {}

        os.makedirs(self.charts_dir, exist_ok=True)

        # Ensure numeric columns
        for col in ["Quantity", "UnitPrice", "TotalAmount"]:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

        print(f"\n📊 Report Generator initialized with {len(self.df)} records")

    # ─────────────────────────────────────────────
    # CHART GENERATORS
    # ─────────────────────────────────────────────

    def chart_revenue_by_category(self):
        """Generate revenue breakdown by category."""
        fig, ax = plt.subplots(figsize=(10, 6))

        if "TotalAmount" not in self.df.columns or "Category" not in self.df.columns:
            return None

        revenue = self.df.groupby("Category")["TotalAmount"].sum().sort_values(ascending=True)
        colors = [CATEGORY_COLORS.get(cat, "#6366f1") for cat in revenue.index]

        bars = ax.barh(revenue.index, revenue.values, color=colors, height=0.6, edgecolor="none")

        # Add value labels
        for bar, val in zip(bars, revenue.values):
            ax.text(val + revenue.max() * 0.02, bar.get_y() + bar.get_height() / 2,
                    f"${val:,.2f}", va="center", fontsize=12, fontweight="bold", color="#e0e0ff")

        ax.set_title("Revenue by Category", fontsize=18, fontweight="bold", pad=20, color="#ffffff")
        ax.set_xlabel("Total Revenue ($)", fontsize=13, labelpad=10)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        path = os.path.join(self.charts_dir, "revenue_by_category.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        self.report_data["revenue_by_category"] = revenue.to_dict()
        print(f"  📈 Generated: revenue_by_category.png")
        return path

    def chart_sales_by_region(self):
        """Generate sales distribution by region."""
        fig, ax = plt.subplots(figsize=(8, 8))

        if "Region" not in self.df.columns:
            return None

        region_counts = self.df["Region"].value_counts()
        colors = ["#6366f1", "#8b5cf6", "#f59e0b", "#10b981"]

        wedges, texts, autotexts = ax.pie(
            region_counts.values,
            labels=region_counts.index,
            autopct="%1.1f%%",
            colors=colors[:len(region_counts)],
            startangle=140,
            pctdistance=0.75,
            wedgeprops={"linewidth": 2, "edgecolor": "#0f0f1a"},
        )

        for text in texts:
            text.set_fontsize(13)
            text.set_fontweight("bold")
        for autotext in autotexts:
            autotext.set_fontsize(11)
            autotext.set_fontweight("bold")

        # Donut effect
        centre_circle = plt.Circle((0, 0), 0.50, fc="#0f0f1a")
        ax.add_patch(centre_circle)
        ax.text(0, 0, f"{len(self.df)}\nOrders", ha="center", va="center",
                fontsize=18, fontweight="bold", color="#e0e0ff")

        ax.set_title("Sales Distribution by Region", fontsize=18, fontweight="bold", pad=20, color="#ffffff")

        plt.tight_layout()
        path = os.path.join(self.charts_dir, "sales_by_region.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        self.report_data["sales_by_region"] = region_counts.to_dict()
        print(f"  📈 Generated: sales_by_region.png")
        return path

    def chart_order_status(self):
        """Generate order status distribution."""
        fig, ax = plt.subplots(figsize=(10, 6))

        if "Status" not in self.df.columns:
            return None

        status_counts = self.df["Status"].value_counts()
        colors = [STATUS_COLORS.get(s, "#6366f1") for s in status_counts.index]

        bars = ax.bar(status_counts.index, status_counts.values, color=colors,
                      width=0.5, edgecolor="none", zorder=3)

        for bar, val in zip(bars, status_counts.values):
            ax.text(bar.get_x() + bar.get_width() / 2, val + 0.3,
                    str(val), ha="center", fontsize=14, fontweight="bold", color="#e0e0ff")

        ax.set_title("Order Status Distribution", fontsize=18, fontweight="bold", pad=20, color="#ffffff")
        ax.set_ylabel("Count", fontsize=13, labelpad=10)
        ax.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        path = os.path.join(self.charts_dir, "order_status.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        self.report_data["order_status"] = status_counts.to_dict()
        print(f"  📈 Generated: order_status.png")
        return path

    def chart_top_products(self, top_n=8):
        """Generate top products by revenue."""
        fig, ax = plt.subplots(figsize=(10, 6))

        if "TotalAmount" not in self.df.columns or "Product" not in self.df.columns:
            return None

        product_revenue = self.df.groupby("Product")["TotalAmount"].sum().nlargest(top_n).sort_values()

        # Gradient colors
        n = len(product_revenue)
        cmap = plt.cm.get_cmap("plasma")
        colors = [cmap(i / n) for i in range(n)]

        bars = ax.barh(product_revenue.index, product_revenue.values, color=colors,
                       height=0.6, edgecolor="none")

        for bar, val in zip(bars, product_revenue.values):
            ax.text(val + product_revenue.max() * 0.02, bar.get_y() + bar.get_height() / 2,
                    f"${val:,.2f}", va="center", fontsize=11, fontweight="bold", color="#e0e0ff")

        ax.set_title(f"Top {top_n} Products by Revenue", fontsize=18, fontweight="bold", pad=20, color="#ffffff")
        ax.set_xlabel("Total Revenue ($)", fontsize=13, labelpad=10)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        path = os.path.join(self.charts_dir, "top_products.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        self.report_data["top_products"] = product_revenue.to_dict()
        print(f"  📈 Generated: top_products.png")
        return path

    def chart_monthly_trend(self):
        """Generate monthly sales trend line chart."""
        fig, ax = plt.subplots(figsize=(12, 6))

        if "OrderDate" not in self.df.columns or "TotalAmount" not in self.df.columns:
            return None

        self.df["OrderDate"] = pd.to_datetime(self.df["OrderDate"], errors="coerce")
        monthly = self.df.dropna(subset=["OrderDate"]).set_index("OrderDate").resample("D")["TotalAmount"].sum()

        if monthly.empty:
            return None

        ax.fill_between(monthly.index, monthly.values, alpha=0.3, color="#6366f1")
        ax.plot(monthly.index, monthly.values, color="#8b5cf6", linewidth=2.5, marker="o",
                markersize=6, markerfacecolor="#c4b5fd", markeredgecolor="#6366f1", zorder=5)

        ax.set_title("Daily Revenue Trend", fontsize=18, fontweight="bold", pad=20, color="#ffffff")
        ax.set_xlabel("Date", fontsize=13, labelpad=10)
        ax.set_ylabel("Revenue ($)", fontsize=13, labelpad=10)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        path = os.path.join(self.charts_dir, "daily_trend.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        print(f"  📈 Generated: daily_trend.png")
        return path

    def chart_price_distribution(self):
        """Generate price distribution histogram."""
        fig, ax = plt.subplots(figsize=(10, 6))

        if "UnitPrice" not in self.df.columns:
            return None

        ax.hist(self.df["UnitPrice"].dropna(), bins=15, color="#6366f1",
                edgecolor="#0f0f1a", alpha=0.85, zorder=3)

        ax.axvline(self.df["UnitPrice"].median(), color="#f59e0b", linestyle="--",
                   linewidth=2, label=f"Median: ${self.df['UnitPrice'].median():,.2f}")
        ax.axvline(self.df["UnitPrice"].mean(), color="#10b981", linestyle="--",
                   linewidth=2, label=f"Mean: ${self.df['UnitPrice'].mean():,.2f}")

        ax.set_title("Unit Price Distribution", fontsize=18, fontweight="bold", pad=20, color="#ffffff")
        ax.set_xlabel("Price ($)", fontsize=13, labelpad=10)
        ax.set_ylabel("Frequency", fontsize=13, labelpad=10)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax.legend(fontsize=11, facecolor="#1a1a2e", edgecolor="#2d2d4a")
        ax.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        path = os.path.join(self.charts_dir, "price_distribution.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        print(f"  📈 Generated: price_distribution.png")
        return path

    # ─────────────────────────────────────────────
    # KPI CALCULATIONS
    # ─────────────────────────────────────────────

    def calculate_kpis(self):
        """Calculate key performance indicators."""
        kpis = {}

        if "TotalAmount" in self.df.columns:
            kpis["total_revenue"] = float(self.df["TotalAmount"].sum())
            kpis["avg_order_value"] = float(self.df["TotalAmount"].mean())
            kpis["max_order_value"] = float(self.df["TotalAmount"].max())
            kpis["min_order_value"] = float(self.df["TotalAmount"].min())

        kpis["total_orders"] = int(len(self.df))

        if "CustomerName" in self.df.columns:
            kpis["unique_customers"] = int(self.df["CustomerName"].nunique())

        if "Product" in self.df.columns:
            kpis["unique_products"] = int(self.df["Product"].nunique())

        if "Status" in self.df.columns:
            completed = len(self.df[self.df["Status"] == "Completed"])
            kpis["completion_rate"] = round(completed / len(self.df) * 100, 1) if len(self.df) > 0 else 0

        if "Quantity" in self.df.columns:
            kpis["total_units_sold"] = int(self.df["Quantity"].sum())

        self.report_data["kpis"] = kpis
        return kpis

    # ─────────────────────────────────────────────
    # HTML REPORT GENERATOR
    # ─────────────────────────────────────────────

    def generate_html_report(self, cleaning_summary=None):
        """Generate a comprehensive HTML report with embedded charts."""
        kpis = self.calculate_kpis()
        chart_paths = []

        print("\n📊 Generating Charts...")
        for method_name in [
            "chart_revenue_by_category",
            "chart_sales_by_region",
            "chart_order_status",
            "chart_top_products",
            "chart_monthly_trend",
            "chart_price_distribution",
        ]:
            method = getattr(self, method_name)
            result = method()
            if result:
                chart_paths.append(result)

        # Build HTML
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        # Chart HTML
        charts_html = ""
        for path in chart_paths:
            fname = os.path.basename(path)
            title = fname.replace(".png", "").replace("_", " ").title()
            charts_html += f"""
            <div class="chart-card">
                <h3>{title}</h3>
                <img src="charts/{fname}" alt="{title}">
            </div>"""

        # Cleaning log HTML
        cleaning_log_html = ""
        if cleaning_summary:
            stats = cleaning_summary.get("stats", {})
            cleaning_log_html = f"""
            <section class="section" id="cleaning-summary">
                <h2>🧹 Data Cleaning Summary</h2>
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-value">{stats.get('original_rows', 0)}</div>
                        <div class="kpi-label">Original Rows</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{stats.get('cleaned_rows', 0)}</div>
                        <div class="kpi-label">Cleaned Rows</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{stats.get('duplicates_removed', 0)}</div>
                        <div class="kpi-label">Duplicates Removed</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{stats.get('missing_values_handled', 0)}</div>
                        <div class="kpi-label">Missing Values Fixed</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{stats.get('inconsistencies_fixed', 0)}</div>
                        <div class="kpi-label">Inconsistencies Fixed</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{stats.get('invalid_entries_fixed', 0)}</div>
                        <div class="kpi-label">Invalid Entries Fixed</div>
                    </div>
                </div>
                <div class="quality-score">
                    <span>Data Quality Score: </span>
                    <strong>{cleaning_summary.get('data_quality_score', 0)}%</strong>
                </div>
            </section>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Cleaning & Analysis Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background: #0a0a1a;
            color: #e0e0ff;
            min-height: 100vh;
        }}

        .header {{
            background: linear-gradient(135deg, #1a1a3e 0%, #0f0f2a 50%, #1a0a3e 100%);
            padding: 3rem 2rem;
            text-align: center;
            border-bottom: 1px solid rgba(99, 102, 241, 0.3);
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                        radial-gradient(circle at 80% 50%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
        }}

        .header h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #a78bfa, #6366f1, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            position: relative;
        }}

        .header .subtitle {{
            font-size: 1rem;
            color: #8888bb;
            font-weight: 400;
            position: relative;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .section {{
            margin-bottom: 2.5rem;
        }}

        .section h2 {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid rgba(99, 102, 241, 0.3);
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}

        .kpi-card {{
            background: linear-gradient(135deg, #1a1a2e, #16162a);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }}

        .kpi-card:hover {{
            border-color: rgba(99, 102, 241, 0.5);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
        }}

        .kpi-value {{
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #a78bfa, #6366f1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .kpi-label {{
            font-size: 0.85rem;
            color: #8888bb;
            margin-top: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 1.5rem;
        }}

        .chart-card {{
            background: linear-gradient(135deg, #1a1a2e, #16162a);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }}

        .chart-card:hover {{
            border-color: rgba(99, 102, 241, 0.5);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
        }}

        .chart-card h3 {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #c4b5fd;
        }}

        .chart-card img {{
            width: 100%;
            border-radius: 8px;
        }}

        .quality-score {{
            background: linear-gradient(135deg, #1a1a2e, #16162a);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            font-size: 1.2rem;
            margin-top: 1rem;
        }}

        .quality-score strong {{
            font-size: 2rem;
            color: #10b981;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            background: #1a1a2e;
            border-radius: 12px;
            overflow: hidden;
        }}

        .data-table thead th {{
            background: rgba(99, 102, 241, 0.15);
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #a78bfa;
            border-bottom: 1px solid rgba(99, 102, 241, 0.2);
        }}

        .data-table tbody td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid rgba(99, 102, 241, 0.1);
            font-size: 0.9rem;
        }}

        .data-table tbody tr:hover {{
            background: rgba(99, 102, 241, 0.05);
        }}

        .footer {{
            text-align: center;
            padding: 2rem;
            color: #555580;
            font-size: 0.85rem;
            border-top: 1px solid rgba(99, 102, 241, 0.15);
            margin-top: 2rem;
        }}

        @media (max-width: 768px) {{
            .chart-grid {{
                grid-template-columns: 1fr;
            }}
            .kpi-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .header h1 {{
                font-size: 1.8rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Data Cleaning & Analysis Report</h1>
        <p class="subtitle">Automated report generated on {timestamp}</p>
    </div>

    <div class="container">
        {cleaning_log_html}

        <section class="section" id="kpis">
            <h2>📈 Key Performance Indicators</h2>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value">${kpis.get('total_revenue', 0):,.2f}</div>
                    <div class="kpi-label">Total Revenue</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{kpis.get('total_orders', 0)}</div>
                    <div class="kpi-label">Total Orders</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">${kpis.get('avg_order_value', 0):,.2f}</div>
                    <div class="kpi-label">Avg Order Value</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{kpis.get('unique_customers', 0)}</div>
                    <div class="kpi-label">Unique Customers</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{kpis.get('unique_products', 0)}</div>
                    <div class="kpi-label">Unique Products</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{kpis.get('completion_rate', 0)}%</div>
                    <div class="kpi-label">Completion Rate</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{kpis.get('total_units_sold', 0)}</div>
                    <div class="kpi-label">Total Units Sold</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">${kpis.get('max_order_value', 0):,.2f}</div>
                    <div class="kpi-label">Highest Order Value</div>
                </div>
            </div>
        </section>

        <section class="section" id="charts">
            <h2>📊 Visual Analysis</h2>
            <div class="chart-grid">
                {charts_html}
            </div>
        </section>

        <section class="section" id="data-preview">
            <h2>📋 Data Preview (First 15 Rows)</h2>
            <div style="overflow-x: auto; border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.2);">
                {self.df.head(15).to_html(classes="data-table", index=False, border=0)}
            </div>
        </section>
    </div>

    <div class="footer">
        <p>Generated by <strong>Data Cleaning & Reporting Automation</strong> &bull; {timestamp}</p>
    </div>
</body>
</html>"""

        report_path = os.path.join(self.output_dir, "report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"\n✅ HTML Report generated: {report_path}")

        # Save report data as JSON
        json_path = os.path.join(self.output_dir, "report_data.json")
        with open(json_path, "w") as f:
            json.dump(self.report_data, f, indent=2, default=str)
        print(f"✅ Report data saved: {json_path}")

        return report_path

    def generate_excel_report(self):
        """Generate a formatted Excel report with multiple sheets."""
        excel_path = os.path.join(self.output_dir, "report.xlsx")

        with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
            # Sheet 1: Full Data
            self.df.to_excel(writer, sheet_name="Cleaned Data", index=False)

            # Sheet 2: Summary by Category
            if "Category" in self.df.columns and "TotalAmount" in self.df.columns:
                cat_summary = self.df.groupby("Category").agg(
                    Orders=("Category", "count"),
                    TotalRevenue=("TotalAmount", "sum"),
                    AvgOrderValue=("TotalAmount", "mean"),
                    TotalQuantity=("Quantity", "sum")
                ).round(2)
                cat_summary.to_excel(writer, sheet_name="Category Summary")

            # Sheet 3: Summary by Region
            if "Region" in self.df.columns and "TotalAmount" in self.df.columns:
                region_summary = self.df.groupby("Region").agg(
                    Orders=("Region", "count"),
                    TotalRevenue=("TotalAmount", "sum"),
                    AvgOrderValue=("TotalAmount", "mean"),
                ).round(2)
                region_summary.to_excel(writer, sheet_name="Region Summary")

            # Sheet 4: Product Performance
            if "Product" in self.df.columns and "TotalAmount" in self.df.columns:
                product_summary = self.df.groupby("Product").agg(
                    Orders=("Product", "count"),
                    TotalRevenue=("TotalAmount", "sum"),
                    AvgPrice=("UnitPrice", "mean"),
                    TotalQuantity=("Quantity", "sum")
                ).round(2).sort_values("TotalRevenue", ascending=False)
                product_summary.to_excel(writer, sheet_name="Product Performance")

            # Sheet 5: KPIs
            kpis = self.calculate_kpis()
            kpi_df = pd.DataFrame([
                {"Metric": k.replace("_", " ").title(), "Value": v}
                for k, v in kpis.items()
            ])
            kpi_df.to_excel(writer, sheet_name="KPIs", index=False)

            # Format worksheets
            workbook = writer.book
            header_format = workbook.add_format({
                "bold": True,
                "font_color": "#ffffff",
                "bg_color": "#6366f1",
                "border": 1,
                "text_wrap": True,
                "valign": "vcenter",
                "align": "center",
            })

            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                worksheet.set_tab_color("#6366f1")

        print(f"✅ Excel Report generated: {excel_path}")
        return excel_path


def generate_reports(cleaned_data_path, output_dir="output/reports", cleaning_summary=None):
    """Run the full report generation pipeline."""
    print("\n" + "=" * 60)
    print("  📊 AUTOMATED REPORT GENERATION")
    print("=" * 60)

    generator = ReportGenerator(cleaned_data_path, output_dir)

    # Generate HTML report with charts
    html_path = generator.generate_html_report(cleaning_summary)

    # Generate Excel report
    excel_path = generator.generate_excel_report()

    print("\n" + "=" * 60)
    print("  ✅ ALL REPORTS GENERATED SUCCESSFULLY")
    print("=" * 60)
    print(f"\n  📄 HTML Report:  {html_path}")
    print(f"  📊 Excel Report: {excel_path}")
    print(f"  📁 Charts Dir:   {os.path.join(output_dir, 'charts')}")
    print()

    return html_path, excel_path


if __name__ == "__main__":
    import sys

    data_path = sys.argv[1] if len(sys.argv) > 1 else "output/cleaned_sales_data.csv"

    # Try to load cleaning summary
    cleaning_summary = None
    log_path = "output/cleaning_log.json"
    if os.path.exists(log_path):
        with open(log_path) as f:
            cleaning_summary = json.load(f)

    generate_reports(data_path, cleaning_summary=cleaning_summary)
