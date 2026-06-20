const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType, ShadingType,
        PageBreak, TableOfContents } = require('docx');
const fs = require('fs');

const blue = "2E5BFF";
const darkText = "1A1A1A";
const grayText = "555555";

const border = { style: BorderStyle.SINGLE, size: 1, color: "D9D9D9" };
const borders = { top: border, bottom: border, left: border, right: border };

function heading1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] });
}
function heading2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
}
function body(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 160 },
    children: [new TextRun({ text, ...opts })]
  });
}
function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 80 },
    children: [new TextRun(text)]
  });
}

function statCell(label, value, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: "F0F4FF", type: ShadingType.CLEAR },
    margins: { top: 160, bottom: 160, left: 160, right: 160 },
    children: [
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: {after: 60}, children: [new TextRun({ text: value, bold: true, size: 28, color: blue })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: label, size: 18, color: grayText })] }),
    ]
  });
}

function dataTable(headers, rows, colWidths) {
  const headerRow = new TableRow({
    children: headers.map((h, i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: blue, type: ShadingType.CLEAR },
      margins: { top: 100, bottom: 100, left: 120, right: 120 },
      children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: "FFFFFF", size: 20 })] })]
    }))
  });
  const bodyRows = rows.map((r, idx) => new TableRow({
    children: r.map((cellText, i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: idx % 2 === 0 ? "FFFFFF" : "F7F9FC", type: ShadingType.CLEAR },
      margins: { top: 90, bottom: 90, left: 120, right: 120 },
      children: [new Paragraph({ children: [new TextRun({ text: String(cellText), size: 20 })] })]
    }))
  }));
  return new Table({
    width: { size: colWidths.reduce((a,b)=>a+b,0), type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...bodyRows]
  });
}

function chartImage(path, widthPx, heightPx) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 240 },
    children: [new ImageRun({
      type: "png",
      data: fs.readFileSync(path),
      transformation: { width: widthPx, height: heightPx }
    })]
  });
}

const insights = JSON.parse(fs.readFileSync('/home/claude/task02/outputs/insights.json', 'utf8'));
const log = JSON.parse(fs.readFileSync('/home/claude/task02/outputs/cleaning_log.json', 'utf8'));

const fmtINR = (n) => "₹" + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22, color: darkText } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: blue },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: darkText },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 }
      }
    },
    children: [
      // TITLE PAGE
      new Paragraph({ spacing: { before: 2400, after: 0 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "RETAIL SALES", bold: true, size: 56, color: blue })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 },
        children: [new TextRun({ text: "Data Cleaning & Business Insights Report", bold: true, size: 36, color: darkText })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
        children: [new TextRun({ text: "Task 02 — Data Cleaning & Business Insights", size: 22, color: grayText })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
        children: [new TextRun({ text: "Prepared June 2026", size: 20, color: grayText })] }),
      new Paragraph({ children: [new PageBreak()] }),

      // EXECUTIVE SUMMARY
      heading1("1. Executive Summary"),
      body("This report documents the end-to-end cleaning of a raw retail sales export and the business insights derived from the cleaned data. The source file contained 1,250 transaction records spanning January 2024 to June 2025, collected across 7 product categories, 4 regions, and 5 payment methods."),
      body("The raw data exhibited common real-world data quality issues: missing values across nearly every column, exact and partial duplicate records, inconsistent text casing and formatting, multiple date formats, and a small number of extreme outliers caused by data entry errors. After cleaning, the dataset was reduced to 1,199 valid, de-duplicated, standardized records ready for analysis."),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2340, 2340, 2340, 2340],
        rows: [ new TableRow({ children: [
          statCell("Total Revenue", fmtINR(insights.total_revenue), 2340),
          statCell("Total Orders", insights.total_orders.toLocaleString('en-IN'), 2340),
          statCell("Avg Order Value", fmtINR(insights.avg_order_value), 2340),
          statCell("Avg Rating", `${insights.avg_rating} / 5`, 2340),
        ]})]
      }),
      new Paragraph({ text: "", spacing: { after: 200 } }),

      heading1("2. Data Cleaning Process"),
      heading2("2.1 Missing Value Handling"),
      body("Missing values were present across nearly every column in the raw export. Each was handled using a method appropriate to that field rather than a single blanket rule:"),
      bullet(`Revenue and Unit Price: where one was missing but enough information existed (price, quantity, discount), the missing value was recalculated from the other fields rather than dropped.`),
      bullet(`Quantity: missing values were imputed using the median quantity for that product category, since order size varies by category.`),
      bullet(`Discount Percent: missing values were filled with 0%, the most common (modal) value in the dataset, representing "no discount applied."`),
      bullet(`Category, Region, City, Payment Method: missing values were labeled "Unknown" rather than dropped, preserving the row for revenue analysis while flagging it for follow-up with the source system.`),
      bullet(`Customer Rating: left as missing where genuinely not provided (a customer choosing not to rate is meaningful), and a HasRating flag column was added so analysts can filter ratings-based metrics correctly.`),
      bullet(`${log.rows_dropped_no_price_no_revenue} row(s) were dropped outright — these had no price and no revenue, making the transaction value unrecoverable.`),

      heading2("2.2 Duplicate Removal"),
      body(`The raw file contained ${log.exact_duplicates_removed} fully exact duplicate rows and ${log.orderid_duplicates_removed} additional rows sharing an Order ID with another record (re-entries differing only in name casing/whitespace — a common symptom of repeated manual entry or a failed retry during export). All duplicates were removed, keeping the first occurrence of each Order ID.`),

      heading2("2.3 Data Formatting & Standardization"),
      body("Several fields had inconsistent formatting that would silently break any group-by analysis if left as-is:"),
      bullet(`Text casing: Category, Region, and Payment Method values appeared in mixed case (e.g. "electronics", "ELECTRONICS", "Electronic") and were mapped to a single canonical label per category.`),
      bullet(`Whitespace: leading/trailing spaces in names and city fields (e.g. "  Meena Choudhary  ") were stripped.`),
      bullet(`Dates: Order Date appeared in five different formats (YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY, DD-Mon-YYYY, YYYY/MM/DD) across different rows — likely from multiple export sources or regional settings. All dates were parsed and standardized to ISO format (YYYY-MM-DD).`),
      bullet(`Customer names and cities were standardized to title case for consistent reporting.`),

      heading2("2.4 Outlier Detection"),
      body("Outliers were detected using the Interquartile Range (IQR) method, with price and revenue evaluated per product category — since a high-end Electronics order and a high-end Books order represent very different things, a single global threshold would have wrongly flagged most electronics sales as outliers."),
      dataTable(
        ["Field", "Method", "Outliers Flagged", "Notes"],
        [
          ["Unit Price", "IQR per category (1.5×)", String(insights.flagged_price_outliers), "Mostly data-entry pricing errors (~50× normal price)"],
          ["Revenue", "IQR per category (1.5×)", String(insights.flagged_revenue_outliers), "Largely legitimate high-quantity/high-value orders, flagged for review not removal"],
          ["Quantity", "IQR global (1.5×)", String(insights.flagged_quantity_outliers), `${log.extreme_quantity_capped} impossible bulk orders (500 units) corrected to category median`],
        ],
        [2200, 2700, 1800, 2660]
      ),
      new Paragraph({ text: "", spacing: { after: 120 } }),
      body(`Negative values were also corrected: ${log.negative_unitprice_corrected} rows had a negative Unit Price and ${log.negative_revenue_corrected} rows had negative Revenue, both clear sign-entry errors. These were corrected to their absolute value rather than dropped, since the rest of the row's data was usable.`),
      body("Rather than deleting all flagged outliers, each affected row carries a boolean flag column (UnitPrice_outlier, Quantity_outlier, Revenue_outlier) in the cleaned dataset. This lets analysts decide whether to include or exclude them per analysis, instead of silently losing potentially legitimate high-value transactions.", { italics: true, color: grayText, size: 20 }),

      heading2("2.5 Cleaning Summary"),
      dataTable(
        ["Metric", "Value"],
        [
          ["Raw rows", String(log.initial_row_count)],
          ["Exact duplicates removed", String(log.exact_duplicates_removed)],
          ["Order ID duplicates removed", String(log.orderid_duplicates_removed)],
          ["Rows dropped (unrecoverable)", String(log.rows_dropped_no_price_no_revenue)],
          ["Final clean rows", String(log.final_row_count)],
          ["Columns in final dataset", "16 (12 original + 4 QA flag columns)"],
        ],
        [5680, 3680]
      ),

      new Paragraph({ children: [new PageBreak()] }),

      // INSIGHTS
      heading1("3. Business Insights"),

      heading2("3.1 Revenue by Category"),
      body(`Electronics dominates total revenue at ${fmtINR(insights.revenue_by_category.Electronics.sum)} from just ${insights.revenue_by_category.Electronics.count} orders — driven by a high average order value of ${fmtINR(insights.revenue_by_category.Electronics.mean)}, roughly 4-20x higher than every other category. Home & Kitchen is a distant second.`),
      chartImage('/home/claude/task02/outputs/chart_revenue_by_category.png', 580, 322),
      bullet(`Highest average order value: ${insights.highest_avg_order_value_category} — high-ticket items drive outsized revenue per transaction.`),
      bullet(`Lowest average order value: ${insights.lowest_avg_order_value_category} — high order count but low basket size; a candidate for bundling or upsell strategies.`),

      heading2("3.2 Revenue by Region"),
      body("Revenue is fairly evenly distributed across all four regions, with North and West marginally ahead. This suggests demand is not geographically concentrated — useful for inventory and logistics planning, as no single region requires disproportionate stock allocation."),
      chartImage('/home/claude/task02/outputs/chart_revenue_by_region.png', 420, 360),

      heading2("3.3 Monthly Revenue Trend"),
      body("Revenue fluctuates month to month without a strong seasonal pattern, with notable peaks in March and October of 2024. The partial 2025-06 figure reflects an incomplete month in the dataset rather than a real decline."),
      chartImage('/home/claude/task02/outputs/chart_monthly_trend.png', 580, 290),

      heading2("3.4 Payment Method Preferences"),
      body(`Cash on Delivery remains the leading payment method by revenue (${fmtINR(insights.revenue_by_payment["Cash on Delivery"].sum)}), narrowly ahead of Net Banking and UPI. Digital payment methods (UPI, Net Banking, Credit/Debit Card) combined account for the majority of revenue, indicating room to incentivize a further shift away from COD — which typically carries higher fulfillment cost and payment risk for the business.`),
      chartImage('/home/claude/task02/outputs/chart_revenue_by_payment.png', 560, 311),

      heading2("3.5 Customer Satisfaction vs. Revenue"),
      body("Average order revenue rises with customer rating up to 4 stars, then dips slightly at 5 stars — suggesting satisfaction is not purely a function of how much a customer spends. Orders rated 1-2 stars still generate substantial average revenue, meaning low ratings are likely driven by service or product issues rather than price dissatisfaction."),
      dataTable(
        ["Rating", "Avg Revenue per Order"],
        Object.entries(insights.avg_revenue_by_rating).map(([k,v]) => [`${k.replace('.0','')} ★`, fmtINR(v)]),
        [4680, 4680]
      ),

      new Paragraph({ text: "", spacing: { after: 160 } }),
      heading2("3.6 Top Performing Cities"),
      body("The top 10 cities by revenue are led by Kochi, followed by Lucknow and Bhubaneswar — a spread across South, North, and East regions rather than concentration in traditional metro hubs like Mumbai or Bengaluru. This is a useful, less-obvious signal for targeted regional marketing."),
      dataTable(
        ["City", "Revenue"],
        Object.entries(insights.top_10_cities).slice(0,6).map(([k,v]) => [k, fmtINR(v)]),
        [4680, 4680]
      ),

      new Paragraph({ children: [new PageBreak()] }),

      heading1("4. Key Recommendations"),
      bullet("Double down on Electronics merchandising and stock depth — it drives the large majority of revenue from a relatively small order count, so even small improvements in conversion or basket size here have outsized impact."),
      bullet("Investigate the Books and Toys categories for bundling, cross-sell, or minimum-order-value promotions to lift their low average order value."),
      bullet("Run a structured campaign to migrate Cash-on-Delivery customers to digital payment methods (e.g. a small UPI cashback) to reduce fulfillment risk and cost."),
      bullet("Audit the data pipeline feeding this export — the volume of missing values, mixed date formats, and duplicate Order IDs suggests multiple source systems or manual re-entry steps that should be consolidated."),
      bullet("Treat rows flagged as outliers (especially the 7 price outliers showing ~50× normal pricing) as a priority data-quality ticket with the source team, since these likely reflect a unit-of-measure or currency entry bug rather than real pricing."),
      bullet("Investigate low-rating (1-2★) orders specifically for service/fulfillment issues, since revenue data shows these aren't simply low-value or discount-driven purchases."),

      heading1("5. Methodology Note"),
      body("All cleaning steps were performed programmatically (Python/pandas) and are fully reproducible via the accompanying script (clean_data.py) and logged in cleaning_log.json. No manual row-by-row edits were made, ensuring the process can be re-run on future data exports with the same logic.", { size: 20, color: grayText }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/home/claude/task02/outputs/Business_Insights_Report.docx', buffer);
  console.log('Report written.');
});
