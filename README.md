# 📊 Task 02 – Data Cleaning & Business Insights

A complete beginner-friendly project that takes a **messy retail sales dataset**, cleans it step by step, and generates **real business insights** with charts and a full report.

---

## 📁 Project Structure

```
task02/
├── data/
│   └── raw_sales_data.csv          ← Messy input dataset (1,250 rows)
├── scripts/
│   ├── generate_messy_data.py      ← Creates the raw dataset with real-world issues
│   ├── clean_data.py               ← Full data cleaning pipeline
│   ├── generate_insights.py        ← Extracts business insights from clean data
│   └── build_report.js             ← Generates the Word report (Node.js)
├── outputs/
│   ├── cleaned_sales_data.csv      ← Final clean dataset (CSV)
│   ├── cleaned_sales_data.xlsx     ← Final clean dataset (Excel, formatted)
│   ├── cleaning_log.json           ← Log of every cleaning step + counts
│   ├── insights.json               ← All KPIs and insights as JSON
│   ├── chart_*.png                 ← Chart images used in report
│   └── Business_Insights_Report.docx ← Final business report (Word)
└── README.md
```

---

## 🧹 What Problems Were in the Raw Data?

| Problem | Example | How It Was Fixed |
|---|---|---|
| Missing values | Empty UnitPrice, Region, City | Recalculated or filled with "Unknown" |
| Exact duplicates | 35 identical rows | Removed with drop_duplicates() |
| Order ID duplicates | 15 re-entered orders | Kept first occurrence per OrderID |
| Inconsistent text | "electronics", "ELECTRONICS", "Electronic" | Mapped to one standard label |
| Multiple date formats | 2024-01-05, 05/01/2024, 05-Jan-2024 | Parsed all formats to ISO YYYY-MM-DD |
| Whitespace in names | "  Meena Choudhary  " | .strip() applied |
| Negative prices | -1042.08 (sign error) | Converted to absolute value |
| Outlier quantities | 500 units (entry error) | Capped using IQR method |

---

## 📈 Key Business Insights Found

- 💰 **Total Revenue**: ₹1.28 Crore across 1,199 orders
- 📱 **Electronics** = 62% of all revenue (avg order ₹48,439)
- 📚 **Books** = most orders but lowest avg value (₹943) — upsell opportunity
- 🚚 **Cash on Delivery** is still the #1 payment method — risk for the business
- 🏙️ **Kochi** is the top-performing city, ahead of Mumbai and Delhi
- ⭐ Orders with 4-star ratings generate the highest average revenue

---

## 🚀 How to Run This Project

### Step 1 – Install Requirements
```bash
pip install pandas numpy matplotlib openpyxl
npm install -g docx
```

### Step 2 – Generate the Messy Dataset
```bash
python scripts/generate_messy_data.py
```

### Step 3 – Clean the Data
```bash
python scripts/clean_data.py
```

### Step 4 – Generate Insights
```bash
python scripts/generate_insights.py
```

### Step 5 – Build the Word Report
```bash
node scripts/build_report.js
```

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| Python 3 | Main scripting language |
| pandas | Data manipulation and cleaning |
| numpy | Numerical operations, IQR outlier detection |
| matplotlib | Chart generation |
| openpyxl | Excel file formatting |
| Node.js + docx | Word report generation |

---

## 📌 Skills Demonstrated

- ✅ Missing Value Handling (multiple strategies per column)
- ✅ Duplicate Detection and Removal (exact + near-duplicate)
- ✅ Data Formatting and Standardization
- ✅ Outlier Detection (IQR method, per-category for price)
- ✅ Business Insight Generation with charts
- ✅ Automated, reproducible pipeline (no manual edits)

---

## 👨‍💻 Beginner Tip

Start by reading `scripts/clean_data.py` top to bottom — each section is labeled and explains what it does and why.

---

*Built as part of Data Analytics Internship – Task 02*
