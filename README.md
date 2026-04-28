# Dashboard Vendite & Profitti
**Interactive Streamlit Dashboard for Sales, Profit, and Logistics Analysis**

## Link to LIVE DEMO >>> https://interactive-app-dashboard-for-sales-analysis.streamlit.app/

## Overview
This advanced Streamlit dashboard enables comprehensive analysis of sales, profit, shipping logistics, product performance, and geographical distribution. Users can upload their own CSV sales data, preview and clean it, and explore a wide range of interactive visualizations and KPIs.

## Key Features

- **Data Upload & Preview:** Upload your sales CSV, preview the first rows, and ensure correct formatting.
- **Automated Data Cleaning:** Handles date parsing, numeric conversion, duplicate removal, and feature engineering (year, month, quarter, shipping delay, etc.).
- **KPIs:** Instantly view total sales, total profit, profit margin, average order value, average profit, and average shipping delay.
- **Monthly Trends:** Interactive line chart of monthly sales by year.
- **Sub-Category Analysis:** Bar charts for sales and profit by product sub-category, with color-coded profit levels.
- **Top States Donut Charts:** Visualize the top 5 states by profit and by losses.
- **Logistics Analysis:** Boxplot and bar chart for shipping delays, highlighting states with the highest average delays.
- **Geographical Map:** Choropleth map of sales by US state, with state labels and downloadable as PNG.
- **Consistent Styling:** All charts use a blue-green palette for clarity and aesthetics.

## Technologies Used

- Streamlit, Pandas, NumPy, Seaborn, Matplotlib, GeoPandas

## Requirements

See `requirements.txt` or install:
```
streamlit pandas numpy seaborn matplotlib geopandas
```

## Usage

1. Run with `streamlit run app.py` in the Dashboard_App directory.
2. Upload your sales CSV (see template for required columns).
3. Explore KPIs, trends, product and logistics analysis, and interactive maps.

## Data Format

Your CSV should include:
- `Order_Date`, `Ship_Date`, `Sales`, `Profit`, `Quantity`, `Category`, `Sub_Category`, `State`

## Notes

- The app requires `us-states.json` for map visualization.
- All processing and visualizations are dynamic and update with your data.

---
