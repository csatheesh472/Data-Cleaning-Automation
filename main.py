"""
Main Pipeline Runner
=====================
Orchestrates the complete data cleaning and reporting workflow.
Run this script to execute the full automation pipeline.
"""

import os
import sys
import json
from data_cleaner import run_cleaning_pipeline
from report_generator import generate_reports


def main():
    """Execute the full data cleaning and reporting pipeline."""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " DATA CLEANING & REPORTING AUTOMATION ".center(58) + "║")
    print("║" + " ─────────────────────────────────── ".center(58) + "║")
    print("║" + " Automated Pipeline Runner ".center(58) + "║")
    print("╚" + "═" * 58 + "╝\n")

    # Configuration
    input_file = os.path.join("sample_data", "raw_sales_data.csv")
    output_dir = "output"
    reports_dir = os.path.join(output_dir, "reports")

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        print("   Please place your CSV or Excel file in the 'sample_data' directory.")
        sys.exit(1)

    # ──────────────────────────────────
    # PHASE 1: DATA CLEANING
    # ──────────────────────────────────
    print("\n🔄 PHASE 1: DATA CLEANING")
    print("─" * 40)
    cleaner, cleaning_summary = run_cleaning_pipeline(input_file, output_dir=output_dir)

    # ──────────────────────────────────
    # PHASE 2: REPORT GENERATION
    # ──────────────────────────────────
    print("\n🔄 PHASE 2: REPORT GENERATION")
    print("─" * 40)
    cleaned_data_path = os.path.join(output_dir, "cleaned_sales_data.csv")
    html_report, excel_report = generate_reports(
        cleaned_data_path,
        output_dir=reports_dir,
        cleaning_summary=cleaning_summary
    )

    # ──────────────────────────────────
    # FINAL SUMMARY
    # ──────────────────────────────────
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " ✅ PIPELINE COMPLETED SUCCESSFULLY ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print(f"""
📁 Output Files:
   ├── {output_dir}/
   │   ├── cleaned_sales_data.csv      (Cleaned data)
   │   ├── cleaned_sales_data.xlsx     (Cleaned data - Excel)
   │   ├── cleaning_log.json           (Cleaning audit log)
   │   └── reports/
   │       ├── report.html             (Visual HTML report)
   │       ├── report.xlsx             (Excel report)
   │       ├── report_data.json        (Report metrics)
   │       └── charts/                 (Chart images)
   │           ├── revenue_by_category.png
   │           ├── sales_by_region.png
   │           ├── order_status.png
   │           ├── top_products.png
   │           ├── daily_trend.png
   │           └── price_distribution.png

🌐 Open the HTML report in your browser to view the dashboard!
""")

    return 0


if __name__ == "__main__":
    sys.exit(main())
