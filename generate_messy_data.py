"""Generate a realistic messy retail sales dataset for Task 02."""
import numpy as np
import pandas as pd
import random

rng = np.random.default_rng(42)
random.seed(42)

N = 1200

categories = ["Electronics", "Clothing", "Home & Kitchen", "Beauty", "Sports", "Books", "Toys"]
cat_variants = {
    "Electronics": ["Electronics", "electronics", "ELECTRONICS", "Electronic"],
    "Clothing": ["Clothing", "clothing", "Cloths", "CLOTHING"],
    "Home & Kitchen": ["Home & Kitchen", "home & kitchen", "Home and Kitchen", "Home&Kitchen"],
    "Beauty": ["Beauty", "beauty", "BEAUTY"],
    "Sports": ["Sports", "sports", "Sport"],
    "Books": ["Books", "books", "BOOKS"],
    "Toys": ["Toys", "toys", "Toy"],
}

regions = ["North", "South", "East", "West"]
region_variants = {
    "North": ["North", "north", "NORTH", "Nort"],
    "South": ["South", "south", "SOUTH"],
    "East": ["East", "east", "EAST"],
    "West": ["West", "west", "WEST", "Wast"],
}

payment_methods = ["Credit Card", "Debit Card", "UPI", "Cash on Delivery", "Net Banking"]
payment_variants = {
    "Credit Card": ["Credit Card", "credit card", "CC", "Credit_Card"],
    "Debit Card": ["Debit Card", "debit card", "DC"],
    "UPI": ["UPI", "upi", "Upi"],
    "Cash on Delivery": ["Cash on Delivery", "COD", "cod", "Cash On Delivery"],
    "Net Banking": ["Net Banking", "net banking", "NetBanking"],
}

first_names = ["Aarav","Priya","Rohan","Sneha","Vikram","Anita","Karan","Divya","Suresh","Meena",
               "Rahul","Pooja","Amit","Neha","Sanjay","Kavita","Arjun","Riya","Manoj","Shreya"]
last_names = ["Sharma","Verma","Patel","Gupta","Reddy","Iyer","Singh","Mehta","Joshi","Nair",
              "Kapoor","Choudhary","Malhotra","Bose","Rao"]

cities = {
    "North": ["Delhi", "Chandigarh", "Jaipur", "Lucknow"],
    "South": ["Bengaluru", "Chennai", "Hyderabad", "Kochi"],
    "East": ["Kolkata", "Bhubaneswar", "Patna", "Guwahati"],
    "West": ["Mumbai", "Pune", "Ahmedabad", "Surat"],
}

date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d-%b-%Y", "%Y/%m/%d"]

rows = []
order_id_start = 100000

for i in range(N):
    cat = random.choice(categories)
    cat_display = random.choice(cat_variants[cat])
    region = random.choice(regions)
    region_display = random.choice(region_variants[region])
    pay = random.choice(payment_methods)
    pay_display = random.choice(payment_variants[pay])

    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    # introduce inconsistent casing/whitespace in names
    if random.random() < 0.15:
        name = name.upper()
    elif random.random() < 0.15:
        name = name.lower()
    if random.random() < 0.1:
        name = "  " + name + "  "

    city = random.choice(cities[region])

    # base price per category (realistic-ish ranges)
    price_ranges = {
        "Electronics": (1500, 60000),
        "Clothing": (300, 4000),
        "Home & Kitchen": (200, 15000),
        "Beauty": (100, 3000),
        "Sports": (200, 8000),
        "Books": (99, 1200),
        "Toys": (150, 3500),
    }
    low, high = price_ranges[cat]
    unit_price = round(rng.uniform(low, high), 2)
    qty = int(rng.choice([1,1,1,2,2,3,4,5], p=[0.35,0.2,0.1,0.15,0.1,0.05,0.03,0.02]))
    discount_pct = round(rng.choice([0,0,0,5,10,15,20,25,30], p=[0.3,0.15,0.1,0.15,0.1,0.08,0.06,0.04,0.02]), 1)

    revenue = round(unit_price * qty * (1 - discount_pct/100), 2)

    # random date in 2024-2025
    days_offset = int(rng.integers(0, 540))
    base_date = pd.Timestamp("2024-01-01") + pd.Timedelta(days=days_offset)
    fmt = random.choice(date_formats)
    date_str = base_date.strftime(fmt)

    order_id = order_id_start + i

    rating = rng.choice([1,2,3,4,5,np.nan], p=[0.03,0.05,0.12,0.35,0.35,0.10])

    row = {
        "OrderID": order_id,
        "CustomerName": name,
        "Category": cat_display,
        "Region": region_display,
        "City": city,
        "OrderDate": date_str,
        "Quantity": qty,
        "UnitPrice": unit_price,
        "DiscountPercent": discount_pct,
        "Revenue": revenue,
        "PaymentMethod": pay_display,
        "CustomerRating": rating,
    }
    rows.append(row)

df = pd.DataFrame(rows)

# --- Inject messiness ---

# 1. Missing values scattered across columns
for col, frac in [("CustomerName", 0.02), ("Category", 0.015), ("Region", 0.01),
                   ("City", 0.02), ("UnitPrice", 0.02), ("Quantity", 0.01),
                   ("DiscountPercent", 0.03), ("PaymentMethod", 0.02), ("Revenue", 0.015)]:
    idx = df.sample(frac=frac, random_state=rng.integers(0, 99999)).index
    df.loc[idx, col] = np.nan

# 2. Duplicate rows (exact duplicates)
dupes = df.sample(n=35, random_state=7)
df = pd.concat([df, dupes], ignore_index=True)

# 3. Near-duplicate rows (same OrderID, slightly different casing) - simulate re-entry errors
near_dupes = df.sample(n=15, random_state=11).copy()
near_dupes["CustomerName"] = near_dupes["CustomerName"].astype(str).str.upper()
df = pd.concat([df, near_dupes], ignore_index=True)

# 4. Outliers: a few absurd unit prices / quantities / revenue
outlier_idx = df.sample(n=12, random_state=3).index
for j, idx in enumerate(outlier_idx):
    if j % 3 == 0:
        df.loc[idx, "UnitPrice"] = df.loc[idx, "UnitPrice"] * 50  # data entry error
    elif j % 3 == 1:
        df.loc[idx, "Quantity"] = 500  # impossible bulk order
    else:
        df.loc[idx, "Revenue"] = -abs(df.loc[idx, "Revenue"])  # negative revenue error

# 5. Some negative/zero prices (entry errors)
neg_idx = df.sample(n=5, random_state=4).index
df.loc[neg_idx, "UnitPrice"] = -df.loc[neg_idx, "UnitPrice"]

# 6. Inconsistent text formatting already injected via variants; add stray whitespace to City
ws_idx = df.sample(n=20, random_state=5).index
df.loc[ws_idx, "City"] = df.loc[ws_idx, "City"].astype(str) + "  "

# shuffle rows
df = df.sample(frac=1, random_state=99).reset_index(drop=True)

df.to_csv("/home/claude/task02/data/raw_sales_data.csv", index=False)
print(f"Generated {len(df)} rows -> data/raw_sales_data.csv")
print(df.isna().sum())
