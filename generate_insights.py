"""Generate business insights from the cleaned sales dataset."""
import pandas as pd
import numpy as np
import json

df = pd.read_csv("/home/claude/task02/outputs/cleaned_sales_data.csv")
df["OrderDate"] = pd.to_datetime(df["OrderDate"])
df["Month"] = df["OrderDate"].dt.to_period("M").astype(str)

insights = {}

# Overall KPIs
insights["total_revenue"] = round(df["Revenue"].sum(), 2)
insights["total_orders"] = len(df)
insights["avg_order_value"] = round(df["Revenue"].mean(), 2)
insights["avg_discount_pct"] = round(df["DiscountPercent"].mean(), 2)
insights["avg_rating"] = round(df["CustomerRating"].mean(), 2)

# Revenue by category
cat_rev = df.groupby("Category")["Revenue"].agg(["sum","mean","count"]).round(2).sort_values("sum", ascending=False)
insights["revenue_by_category"] = cat_rev.to_dict(orient="index")

# Revenue by region
region_rev = df.groupby("Region")["Revenue"].agg(["sum","mean","count"]).round(2).sort_values("sum", ascending=False)
insights["revenue_by_region"] = region_rev.to_dict(orient="index")

# Revenue by payment method
pay_rev = df.groupby("PaymentMethod")["Revenue"].agg(["sum","count"]).round(2).sort_values("sum", ascending=False)
insights["revenue_by_payment"] = pay_rev.to_dict(orient="index")

# Monthly trend
monthly = df.groupby("Month")["Revenue"].sum().round(2)
insights["monthly_revenue"] = monthly.to_dict()

# Top cities
city_rev = df.groupby("City")["Revenue"].sum().round(2).sort_values(ascending=False).head(10)
insights["top_10_cities"] = city_rev.to_dict()

# Discount impact: does higher discount correlate with higher quantity sold?
discount_qty_corr = df["DiscountPercent"].corr(df["Quantity"])
insights["discount_quantity_correlation"] = round(float(discount_qty_corr), 3)

# Rating vs Revenue
rating_rev = df.dropna(subset=["CustomerRating"]).groupby("CustomerRating")["Revenue"].mean().round(2)
insights["avg_revenue_by_rating"] = rating_rev.to_dict()

# Outlier orders flagged
insights["flagged_price_outliers"] = int(df["UnitPrice_outlier"].sum())
insights["flagged_revenue_outliers"] = int(df["Revenue_outlier"].sum())
insights["flagged_quantity_outliers"] = int(df["Quantity_outlier"].sum())

# Category with best avg order value
insights["highest_avg_order_value_category"] = cat_rev["mean"].idxmax()
insights["lowest_avg_order_value_category"] = cat_rev["mean"].idxmin()

# Best performing region by avg order value
insights["highest_avg_order_value_region"] = region_rev["mean"].idxmax()

with open("/home/claude/task02/outputs/insights.json", "w") as f:
    json.dump(insights, f, indent=2, default=str)

print(json.dumps(insights, indent=2, default=str))
