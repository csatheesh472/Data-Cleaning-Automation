"""
Data Cleaning Automation Module
================================
Handles missing values, duplicates, inconsistent formatting,
invalid entries, and data standardization.
"""

import pandas as pd
import numpy as np
import re
import os
import json
from datetime import datetime


class DataCleaner:
    """Automated data cleaning pipeline with comprehensive logging."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.original_df = None
        self.cleaned_df = None
        self.cleaning_log = []
        self.stats = {
            "original_rows": 0,
            "original_cols": 0,
            "cleaned_rows": 0,
            "cleaned_cols": 0,
            "duplicates_removed": 0,
            "missing_values_handled": 0,
            "inconsistencies_fixed": 0,
            "invalid_entries_fixed": 0,
        }

    def load_data(self):
        """Load data from CSV or Excel file."""
        ext = os.path.splitext(self.filepath)[1].lower()

        if ext == ".csv":
            self.original_df = pd.read_csv(self.filepath)
        elif ext in [".xlsx", ".xls"]:
            self.original_df = pd.read_excel(self.filepath)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        self.cleaned_df = self.original_df.copy()
        self.stats["original_rows"] = len(self.original_df)
        self.stats["original_cols"] = len(self.original_df.columns)
        self._log(f"✅ Loaded {len(self.original_df)} rows and {len(self.original_df.columns)} columns from '{os.path.basename(self.filepath)}'")
        return self

    def _log(self, message):
        """Add entry to cleaning log with timestamp."""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": message
        }
        self.cleaning_log.append(entry)
        print(f"  [{entry['timestamp']}] {message}")

    # ─────────────────────────────────────────────
    # 1. DUPLICATE HANDLING
    # ─────────────────────────────────────────────
    def remove_duplicates(self, subset=None, keep="first"):
        """Remove duplicate rows based on specified columns."""
        before = len(self.cleaned_df)
        self.cleaned_df = self.cleaned_df.drop_duplicates(subset=subset, keep=keep)
        removed = before - len(self.cleaned_df)
        self.stats["duplicates_removed"] = removed

        if removed > 0:
            self._log(f"🗑️  Removed {removed} duplicate rows (subset={subset}, keep='{keep}')")
        else:
            self._log("✅ No duplicate rows found")
        return self

    # ─────────────────────────────────────────────
    # 2. MISSING VALUE HANDLING
    # ─────────────────────────────────────────────
    def handle_missing_values(self, strategy="auto", fill_values=None):
        """
        Handle missing values with multiple strategies.
        
        Strategies:
        - 'auto': Numeric cols -> median, Categorical cols -> mode
        - 'drop': Drop rows with any missing values
        - 'fill': Use fill_values dict for specific columns
        - 'interpolate': Use interpolation for numeric columns
        """
        missing_before = self.cleaned_df.isnull().sum().sum()

        if strategy == "auto":
            for col in self.cleaned_df.columns:
                missing_count = self.cleaned_df[col].isnull().sum()
                if missing_count > 0:
                    if self.cleaned_df[col].dtype in ["int64", "float64"]:
                        median_val = self.cleaned_df[col].median()
                        self.cleaned_df[col].fillna(median_val, inplace=True)
                        self._log(f"📊 Filled {missing_count} missing values in '{col}' with median ({median_val})")
                    else:
                        if not self.cleaned_df[col].mode().empty:
                            mode_val = self.cleaned_df[col].mode()[0]
                            self.cleaned_df[col].fillna(mode_val, inplace=True)
                            self._log(f"📊 Filled {missing_count} missing values in '{col}' with mode ('{mode_val}')")
                        else:
                            self.cleaned_df[col].fillna("Unknown", inplace=True)
                            self._log(f"📊 Filled {missing_count} missing values in '{col}' with 'Unknown'")

        elif strategy == "drop":
            self.cleaned_df.dropna(inplace=True)
            self._log(f"🗑️  Dropped rows with missing values")

        elif strategy == "fill" and fill_values:
            for col, val in fill_values.items():
                if col in self.cleaned_df.columns:
                    count = self.cleaned_df[col].isnull().sum()
                    self.cleaned_df[col].fillna(val, inplace=True)
                    self._log(f"📊 Filled {count} missing values in '{col}' with '{val}'")

        elif strategy == "interpolate":
            for col in self.cleaned_df.select_dtypes(include=[np.number]).columns:
                count = self.cleaned_df[col].isnull().sum()
                if count > 0:
                    self.cleaned_df[col].interpolate(method="linear", inplace=True)
                    self._log(f"📊 Interpolated {count} missing values in '{col}'")

        missing_after = self.cleaned_df.isnull().sum().sum()
        self.stats["missing_values_handled"] = missing_before - missing_after
        return self

    # ─────────────────────────────────────────────
    # 3. TEXT STANDARDIZATION
    # ─────────────────────────────────────────────
    def standardize_text(self, columns=None, case="title"):
        """
        Standardize text columns to consistent casing.
        
        Cases: 'title', 'lower', 'upper', 'capitalize'
        """
        if columns is None:
            columns = self.cleaned_df.select_dtypes(include=["object"]).columns.tolist()

        fixes = 0
        for col in columns:
            if col in self.cleaned_df.columns:
                original = self.cleaned_df[col].copy()
                self.cleaned_df[col] = self.cleaned_df[col].astype(str).str.strip()

                if case == "title":
                    self.cleaned_df[col] = self.cleaned_df[col].str.title()
                elif case == "lower":
                    self.cleaned_df[col] = self.cleaned_df[col].str.lower()
                elif case == "upper":
                    self.cleaned_df[col] = self.cleaned_df[col].str.upper()
                elif case == "capitalize":
                    self.cleaned_df[col] = self.cleaned_df[col].str.capitalize()

                changed = (original.astype(str) != self.cleaned_df[col]).sum()
                fixes += changed
                if changed > 0:
                    self._log(f"📝 Standardized {changed} entries in '{col}' to {case} case")

        self.stats["inconsistencies_fixed"] += fixes
        return self

    # ─────────────────────────────────────────────
    # 4. DATE STANDARDIZATION
    # ─────────────────────────────────────────────
    def standardize_dates(self, date_columns, target_format="%Y-%m-%d"):
        """Parse and standardize date columns to a consistent format."""
        for col in date_columns:
            if col in self.cleaned_df.columns:
                original = self.cleaned_df[col].copy()
                # Replace N/A, empty strings with NaT
                self.cleaned_df[col] = self.cleaned_df[col].replace(["N/A", "n/a", "NA", ""], np.nan)
                self.cleaned_df[col] = pd.to_datetime(self.cleaned_df[col], format="mixed", errors="coerce")

                invalid_count = self.cleaned_df[col].isna().sum() - original.isna().sum()
                valid_count = self.cleaned_df[col].notna().sum()

                self._log(f"📅 Standardized {valid_count} dates in '{col}' to '{target_format}' format")
                if invalid_count > 0:
                    self._log(f"⚠️  {invalid_count} unparseable dates in '{col}' set to NaT")

                self.stats["inconsistencies_fixed"] += max(0, valid_count)
        return self

    # ─────────────────────────────────────────────
    # 5. VALIDATE NUMERIC RANGES
    # ─────────────────────────────────────────────
    def validate_numeric_ranges(self, rules):
        """
        Validate numeric columns against defined rules.
        
        rules: dict of {column: {"min": val, "max": val, "action": "clip"|"null"|"drop"}}
        """
        for col, rule in rules.items():
            if col not in self.cleaned_df.columns:
                continue

            min_val = rule.get("min", None)
            max_val = rule.get("max", None)
            action = rule.get("action", "clip")

            mask = pd.Series([False] * len(self.cleaned_df))
            if min_val is not None:
                mask |= self.cleaned_df[col] < min_val
            if max_val is not None:
                mask |= self.cleaned_df[col] > max_val

            invalid_count = mask.sum()

            if invalid_count > 0:
                if action == "clip":
                    if min_val is not None:
                        self.cleaned_df.loc[self.cleaned_df[col] < min_val, col] = min_val
                    if max_val is not None:
                        self.cleaned_df.loc[self.cleaned_df[col] > max_val, col] = max_val
                    self._log(f"🔧 Clipped {invalid_count} out-of-range values in '{col}' to [{min_val}, {max_val}]")
                elif action == "null":
                    self.cleaned_df.loc[mask, col] = np.nan
                    self._log(f"🔧 Set {invalid_count} out-of-range values in '{col}' to null")
                elif action == "drop":
                    self.cleaned_df = self.cleaned_df[~mask]
                    self._log(f"🗑️  Dropped {invalid_count} rows with out-of-range values in '{col}'")

                self.stats["invalid_entries_fixed"] += invalid_count
        return self

    # ─────────────────────────────────────────────
    # 6. EMAIL VALIDATION
    # ─────────────────────────────────────────────
    def validate_emails(self, email_column="Email"):
        """Validate email format and flag invalid entries."""
        if email_column not in self.cleaned_df.columns:
            return self

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        invalid_mask = ~self.cleaned_df[email_column].astype(str).str.match(email_pattern, na=False)
        invalid_mask &= self.cleaned_df[email_column].notna()

        invalid_count = invalid_mask.sum()
        if invalid_count > 0:
            self.cleaned_df.loc[invalid_mask, email_column] = np.nan
            self._log(f"📧 Flagged {invalid_count} invalid email addresses in '{email_column}'")
            self.stats["invalid_entries_fixed"] += invalid_count
        else:
            self._log(f"✅ All emails in '{email_column}' are valid")
        return self

    # ─────────────────────────────────────────────
    # 7. ADD COMPUTED COLUMNS
    # ─────────────────────────────────────────────
    def add_computed_columns(self, computations):
        """
        Add calculated columns to the dataset.
        
        computations: dict of {new_col_name: lambda_function}
        """
        for col_name, func in computations.items():
            try:
                self.cleaned_df[col_name] = func(self.cleaned_df)
                self._log(f"➕ Added computed column '{col_name}'")
            except Exception as e:
                self._log(f"⚠️  Failed to add '{col_name}': {str(e)}")
        return self

    # ─────────────────────────────────────────────
    # 8. EXPORT CLEANED DATA
    # ─────────────────────────────────────────────
    def export(self, output_path, format="csv"):
        """Export cleaned data to CSV or Excel."""
        self.stats["cleaned_rows"] = len(self.cleaned_df)
        self.stats["cleaned_cols"] = len(self.cleaned_df.columns)

        if format == "csv":
            self.cleaned_df.to_csv(output_path, index=False)
        elif format == "excel":
            self.cleaned_df.to_excel(output_path, index=False, engine="openpyxl")

        self._log(f"💾 Exported cleaned data to '{os.path.basename(output_path)}' ({self.stats['cleaned_rows']} rows, {self.stats['cleaned_cols']} cols)")
        return self

    def get_summary(self):
        """Return a comprehensive cleaning summary."""
        return {
            "stats": self.stats,
            "log": self.cleaning_log,
            "data_quality_score": self._calculate_quality_score()
        }

    def _calculate_quality_score(self):
        """Calculate a data quality score (0-100) after cleaning."""
        if self.cleaned_df is None:
            return 0

        total_cells = self.cleaned_df.shape[0] * self.cleaned_df.shape[1]
        missing_cells = self.cleaned_df.isnull().sum().sum()
        completeness = (1 - missing_cells / total_cells) * 100 if total_cells > 0 else 0

        return round(completeness, 1)


def run_cleaning_pipeline(input_path, output_dir="output"):
    """Execute the full data cleaning pipeline."""
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("  🧹 DATA CLEANING AUTOMATION PIPELINE")
    print("=" * 60 + "\n")

    cleaner = DataCleaner(input_path)

    # Step 1: Load
    cleaner.load_data()

    # Step 2: Remove Duplicates
    print("\n── Step 1: Removing Duplicates ──")
    cleaner.remove_duplicates(subset=["CustomerName", "Product", "OrderDate"], keep="first")

    # Step 3: Standardize Text
    print("\n── Step 2: Standardizing Text ──")
    cleaner.standardize_text(columns=["CustomerName", "Product", "Category", "Region", "Status"], case="title")

    # Step 4: Standardize Dates
    print("\n── Step 3: Standardizing Dates ──")
    cleaner.standardize_dates(date_columns=["OrderDate"])

    # Step 5: Handle Missing Values
    print("\n── Step 4: Handling Missing Values ──")
    cleaner.handle_missing_values(strategy="auto")

    # Step 6: Validate Numeric Ranges
    print("\n── Step 5: Validating Numeric Ranges ──")
    cleaner.validate_numeric_ranges({
        "Quantity": {"min": 1, "max": 1000, "action": "clip"},
        "UnitPrice": {"min": 0.01, "max": 100000, "action": "clip"}
    })

    # Step 7: Validate Emails
    print("\n── Step 6: Validating Emails ──")
    cleaner.validate_emails(email_column="Email")

    # Step 8: Add Computed Columns
    print("\n── Step 7: Adding Computed Columns ──")
    cleaner.add_computed_columns({
        "TotalAmount": lambda df: df["Quantity"] * df["UnitPrice"],
        "OrderMonth": lambda df: pd.to_datetime(df["OrderDate"], errors="coerce").dt.strftime("%B %Y"),
    })

    # Step 9: Export
    print("\n── Step 8: Exporting Results ──")
    csv_path = os.path.join(output_dir, "cleaned_sales_data.csv")
    excel_path = os.path.join(output_dir, "cleaned_sales_data.xlsx")
    cleaner.export(csv_path, format="csv")
    cleaner.export(excel_path, format="excel")

    # Save cleaning log as JSON
    summary = cleaner.get_summary()
    log_path = os.path.join(output_dir, "cleaning_log.json")
    with open(log_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("\n" + "=" * 60)
    print(f"  📊 CLEANING SUMMARY")
    print("=" * 60)
    print(f"  Original:  {summary['stats']['original_rows']} rows × {summary['stats']['original_cols']} cols")
    print(f"  Cleaned:   {summary['stats']['cleaned_rows']} rows × {summary['stats']['cleaned_cols']} cols")
    print(f"  Duplicates Removed:      {summary['stats']['duplicates_removed']}")
    print(f"  Missing Values Handled:  {summary['stats']['missing_values_handled']}")
    print(f"  Inconsistencies Fixed:   {summary['stats']['inconsistencies_fixed']}")
    print(f"  Invalid Entries Fixed:   {summary['stats']['invalid_entries_fixed']}")
    print(f"  Data Quality Score:      {summary['data_quality_score']}%")
    print("=" * 60 + "\n")

    return cleaner, summary


if __name__ == "__main__":
    input_file = os.path.join("sample_data", "raw_sales_data.csv")
    cleaner, summary = run_cleaning_pipeline(input_file, output_dir="output")
