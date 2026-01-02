# N-AIRS Power BI Dashboard

## Market Intelligence Command Center

### Overview
The N-AIRS Power BI Dashboard is the analytics and decision-consumption layer of the N-AIRS platform. It provides a consolidated, executive-facing view of:

- Market signal activity
- Decision engine behavior
- Signal performance
- Data quality and pipeline trust

The dashboard is designed to be read-only, explainable, and stable, consuming data exclusively from the Gold Layer (reporting views) in MySQL.

---

## Design Objectives
The dashboard is built to answer five core questions:

1) Is the system active and healthy?
2) How confident and accurate are the generated signals?
3) What actions does the system recommend right now?
4) Why were those actions generated?
5) Can the underlying data be trusted?

Visual design prioritizes clarity over decoration, following internal enterprise dashboard standards.

---

## Data Source & Modeling
### Data Source
- Database: MySQL (nairs)
- Consumption Layer: Gold Layer (Reporting Views)

### Tables / Views Used
The dashboard connects only to the following objects:
- fact_signals
- dim_calendar
- dim_stocks
- rpt_quality_summary

Raw and intermediate pipeline tables are intentionally not exposed to Power BI.

### Semantic Model (Star Schema)
The dashboard uses a star schema to ensure consistent filtering and performance.

#### Relationships
- dim_calendar.date_key → fact_signals.trade_date (One-to-Many)
- dim_stocks.stock_symbol → fact_signals.stock_symbol (One-to-Many)
- dim_calendar.date_key → rpt_quality_summary.trade_date (One-to-Many)
- dim_stocks.stock_symbol → rpt_quality_summary.stock_symbol (One-to-Many)

This model enables clean time-based analysis and stock-level slicing.

---

## Dashboard Layout
The dashboard consists of a single executive page, structured as follows:

### Row 1 — KPI Snapshot
Purpose: Immediate system health and credibility check.

**Metrics Displayed**
- Total Signals: Total number of generated signals in the selected date range.
- Signals Accuracy (%): Percentage of signals resulting in a WIN outcome.
- Avg Signal Confidence: Mean confidence score across generated signals.
- Total Anomalies: Total detected data quality anomalies in the selected period.

These KPIs provide a high-level operational summary without requiring detailed inspection.

### Row 2 — Market & Decision Behavior
- Signal Trend
  - Visual: Area / Line Chart
  - X-axis: Date (dim_calendar.date_key)
  - Y-axis: Signal volume
  - Shows how signal activity changes over time in response to market conditions.

- Decision % by Action
  - Visual: Column Chart
  - X-axis: Action (BUY / SELL / HOLD / WATCH)
  - Y-axis: Percentage of total signals
  - Highlights the decision engine’s behavioral bias (e.g., conservative vs aggressive).

- Reason Code Distribution
  - Visual: Horizontal Bar Chart
  - Dimension: Reason Code
  - Metric: Signal count
  - Provides explainability by showing which technical indicators or rule triggers dominate decisions.

### Row 3 — Actionable Signals
- Top Signals Table
  - Displays the most relevant signals based on confidence.
  - Columns: Trade Date, Stock Symbol, Action, Confidence Score, Reason Code, Return (10d)
  - Signals are sorted by confidence to surface the most actionable recommendations first.

### Filters (Global)
- Date Range
- Stock Symbol
- Action Type

Filters affect all visuals, enabling focused analysis without changing the dashboard structure.

### Row 4 — Data Quality & Trust
- Quality Heat Indicator
  - Visual: Table
  - Metric: Average anomaly count per stock
  - This section answers: “Can today’s signals be trusted?”
  - Stocks with higher anomaly counts can be flagged for caution or investigation.

---

## Measures & Metrics
Key measures are implemented in DAX, including:
- Total Signals
- Signal Accuracy %
- Average Confidence
- Decision Distribution %
- Aggregated anomaly counts

All business logic is centralized upstream in the pipeline or Gold Layer, keeping DAX lightweight and interpretable.

---

## Design Principles Followed
- Single-page executive overview
- No direct dependency on raw tables
- Minimal color usage; color only where meaning exists
- Clear separation of signal generation, performance, and data quality
- Fully explainable decision logic

---

## Intended Users
- Data Analysts
- Product Managers
- Quant / Research Analysts
- Engineering reviewers
- Interview and portfolio reviewers

The dashboard is designed to support both daily monitoring and strategic review.

---

## Limitations
- Dashboard reflects rule-based signal logic, not ML predictions
- Accuracy metrics depend on outcome evaluation windows
- Benchmark comparison (Buy & Hold) is planned but not yet included

These are known design boundaries, not defects.

---

## Future Enhancements
Planned improvements include:
- Benchmark performance comparison
- Sector-level aggregation
- Deep-dive feature correlation page
- Alerting based on anomaly thresholds
- Materialized reporting views for scale

---

## Summary
The N-AIRS Power BI Dashboard serves as the final consumption layer of the N-AIRS data platform. It translates complex pipeline outputs into trustworthy, explainable, and actionable insights while maintaining strict separation between engineering internals and analytics consumption.
