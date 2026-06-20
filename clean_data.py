"""
Task 02: Data Cleaning Pipeline
Cleans the messy retail sales dataset and outputs a clean CSV + a cleaning log.
"""
import pandas as pd
import numpy as np
import json

RAW_PATH = "/home/claude/task02/data/raw_sales_data.csv"
CLEAN_PATH = "/home/claude/task02/outputs/cleaned_sales_data.csv"
LOG_PATH = "/home/claude/task02/outputs/cleaning_log.json"

log = {}

df = pd.read_csv(RAW_PATH)
log["initial_row_count"] = len(df)
log["initial_columns"] = list(df.columns)
log["initial_missing_by_column"] = df.isna().sum().to_dict()

# ---------------------------------------------------------------
# 1. DUPLICATE REMOVAL
# ---------------------------------------------------------------
exact_dupes = df.duplicated().sum()
df = df.drop_duplicates()
log["exact_duplicates_removed"] = int(exact_dupes)

# Near-duplicates: same OrderID appearing more than once (re-entry of same order,
# differing only in text casing/whitespace) -> keep first occurrence
before = len(df)
df = df.sort_values("OrderID")
order_id_dupes = df.duplicated(subset=["OrderID"]).sum()
df = df.drop_duplicates(subset=["OrderID"], keep="first")
log["orderid_duplicates_removed"] = int(order_id_dupes)
log["rows_after_dedup"] = len(df)

# ---------------------------------------------------------------
# 2. DATA FORMATTING (text standardization, whitespace, casing, dates)
# ---------------------------------------------------------------

# Strip whitespace + standardize casing for text columns
text_cols = ["CustomerName", "Category", "Region", "City", "PaymentMethod"]
for col in text_cols:
    df[col] = df[col].astype(str).str.strip()
    df[col] = df[col].replace({"nan": np.nan})

# Title-case names and cities
df["CustomerName"] = df["CustomerName"].str.title()
df["City"] = df["City"].str.title()

# Standardize Category values (map all variants to canonical form)
category_map = {
    "electronics": "Electronics", "electronic": "Electronics",
    "clothing": "Clothing", "cloths": "Clothing",
    "home & kitchen": "Home & Kitchen", "home and kitchen": "Home & Kitchen", "home&kitchen": "Home & Kitchen",
    "beauty": "Beauty",
    "sports": "Sports", "sport": "Sports",
    "books": "Books",
    "toys": "Toys", "toy": "Toys",
}
df["Category"] = df["Category"].str.lower().map(category_map).fillna(df["Category"])

# Standardize Region values
region_map = {
    "north": "North", "nort": "North",
    "south": "South",
    "east": "East",
    "west": "West", "wast": "West",
}
df["Region"] = df["Region"].str.lower().map(region_map).fillna(df["Region"])

# Standardize PaymentMethod values
payment_map = {
    "credit card": "Credit Card", "cc": "Credit Card", "credit_card": "Credit Card",
    "debit card": "Debit Card", "dc": "Debit Card",
    "upi": "UPI",
    "cash on delivery": "Cash on Delivery", "cod": "Cash on Delivery",
    "net banking": "Net Banking", "netbanking": "Net Banking",
}
df["PaymentMethod"] = df["PaymentMethod"].str.lower().map(payment_map).fillna(df["PaymentMethod"])

# Parse OrderDate from multiple formats into a single ISO format
def parse_date(val):
    if pd.isna(val):
        return pd.NaT
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d-%b-%Y", "%Y/%m/%d"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.to_datetime(val, errors="coerce", dayfirst=True)

df["OrderDate"] = df["OrderDate"].apply(parse_date)
log["unparseable_dates"] = int(df["OrderDate"].isna().sum())

# ---------------------------------------------------------------
# 3. MISSING VALUE HANDLING
# ---------------------------------------------------------------
missing_before = df.isna().sum().to_dict()

# Numeric columns: Quantity, UnitPrice, DiscountPercent, Revenue
# Drop rows where critical identifying fields are missing AND unrecoverable
critical_missing = df[df["UnitPrice"].isna() & df["Revenue"].isna()]
log["rows_dropped_no_price_no_revenue"] = len(critical_missing)
df = df[~(df["UnitPrice"].isna() & df["Revenue"].isna())]

# Recompute Revenue where missing but UnitPrice/Quantity/Discount available
mask = df["Revenue"].isna() & df["UnitPrice"].notna() & df["Quantity"].notna()
df.loc[mask, "Revenue"] = (
    df.loc[mask, "UnitPrice"] * df.loc[mask, "Quantity"] *
    (1 - df.loc[mask, "DiscountPercent"].fillna(0) / 100)
).round(2)

# Recompute UnitPrice where missing but Revenue/Quantity available
mask2 = df["UnitPrice"].isna() & df["Revenue"].notna() & df["Quantity"].notna() & (df["Quantity"] > 0)
df.loc[mask2, "UnitPrice"] = (df.loc[mask2, "Revenue"] / df.loc[mask2, "Quantity"]).round(2)

# Quantity missing -> impute with median quantity for that Category
df["Quantity"] = df.groupby("Category")["Quantity"].transform(lambda x: x.fillna(x.median()))
df["Quantity"] = df["Quantity"].fillna(df["Quantity"].median())

# DiscountPercent missing -> assume no discount (0), the most common value
df["DiscountPercent"] = df["DiscountPercent"].fillna(0)

# Categorical missing -> fill with "Unknown"
for col in ["Category", "Region", "City", "PaymentMethod"]:
    df[col] = df[col].fillna("Unknown")

# CustomerName missing -> fill with "Unknown Customer"
df["CustomerName"] = df["CustomerName"].fillna("Unknown Customer")

# CustomerRating missing -> leave as NaN (no rating given), but flag with a boolean column
df["HasRating"] = df["CustomerRating"].notna()

log["missing_after_handling"] = df.isna().sum().to_dict()

# ---------------------------------------------------------------
# 4. OUTLIER DETECTION (IQR method on UnitPrice, Quantity, Revenue)
# ---------------------------------------------------------------
outlier_summary = {}

def iqr_bounds(series):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr

# Fix obviously invalid values first: negative prices/revenue are data entry errors -> take abs
neg_price_count = (df["UnitPrice"] < 0).sum()
df.loc[df["UnitPrice"] < 0, "UnitPrice"] = df.loc[df["UnitPrice"] < 0, "UnitPrice"].abs()
neg_revenue_count = (df["Revenue"] < 0).sum()
df.loc[df["Revenue"] < 0, "Revenue"] = df.loc[df["Revenue"] < 0, "Revenue"].abs()
log["negative_unitprice_corrected"] = int(neg_price_count)
log["negative_revenue_corrected"] = int(neg_revenue_count)

# NOTE: Price ranges differ hugely by Category (e.g. Electronics vs Books), so a single
# global IQR bound would flag legitimate high-ticket electronics as "outliers". We compute
# IQR bounds PER CATEGORY for UnitPrice and Revenue, which is the more realistic approach
# for this kind of multi-category retail dataset. Quantity is evaluated globally since
# order size doesn't vary meaningfully by category.
for col in ["UnitPrice", "Revenue"]:
    bounds = df.groupby("Category")[col].apply(iqr_bounds)
    outlier_flags = pd.Series(False, index=df.index)
    cat_bounds_log = {}
    for cat, (lo, hi) in bounds.items():
        cat_mask = df["Category"] == cat
        flagged = cat_mask & ((df[col] < lo) | (df[col] > hi))
        outlier_flags |= flagged
        cat_bounds_log[cat] = {
            "lower_bound": round(float(lo), 2),
            "upper_bound": round(float(hi), 2),
            "outlier_count": int(flagged.sum()),
        }
    df[f"{col}_outlier"] = outlier_flags
    outlier_summary[col] = {
        "method": "IQR per category (1.5x)",
        "by_category": cat_bounds_log,
        "total_outlier_count": int(outlier_flags.sum()),
    }

lo, hi = iqr_bounds(df["Quantity"])
qty_flagged = (df["Quantity"] < lo) | (df["Quantity"] > hi)
df["Quantity_outlier"] = qty_flagged
outlier_summary["Quantity"] = {
    "method": "IQR global (1.5x)",
    "lower_bound": round(float(lo), 2),
    "upper_bound": round(float(hi), 2),
    "total_outlier_count": int(qty_flagged.sum()),
}

log["outlier_summary"] = outlier_summary

# Cap extreme outliers (winsorize) for Quantity (impossible bulk orders e.g. 500 units)
extreme_qty = df["Quantity"] > (hi * 3)  # only the truly impossible ones (uses Quantity lo/hi from above)
log["extreme_quantity_capped"] = int(extreme_qty.sum())
df.loc[extreme_qty, "Quantity"] = df["Quantity"].median()

# Recompute revenue for rows where quantity was capped
df.loc[extreme_qty, "Revenue"] = (
    df.loc[extreme_qty, "UnitPrice"] * df.loc[extreme_qty, "Quantity"] *
    (1 - df.loc[extreme_qty, "DiscountPercent"] / 100)
).round(2)

# ---------------------------------------------------------------
# Final formatting touches
# ---------------------------------------------------------------
df["UnitPrice"] = df["UnitPrice"].round(2)
df["Revenue"] = df["Revenue"].round(2)
df["Quantity"] = df["Quantity"].astype(int)
df["OrderDate"] = pd.to_datetime(df["OrderDate"]).dt.strftime("%Y-%m-%d")
df["CustomerRating"] = df["CustomerRating"].astype("Int64")

# Reorder columns sensibly
cols_order = ["OrderID", "CustomerName", "Category", "Region", "City", "OrderDate",
              "Quantity", "UnitPrice", "DiscountPercent", "Revenue", "PaymentMethod",
              "CustomerRating", "HasRating", "UnitPrice_outlier", "Quantity_outlier", "Revenue_outlier"]
df = df[cols_order]

df = df.sort_values("OrderDate").reset_index(drop=True)

log["final_row_count"] = len(df)
log["final_missing_by_column"] = df.isna().sum().to_dict()

df.to_csv(CLEAN_PATH, index=False)
with open(LOG_PATH, "w") as f:
    json.dump(log, f, indent=2, default=str)

print("Cleaning complete.")
print(json.dumps(log, indent=2, default=str))
