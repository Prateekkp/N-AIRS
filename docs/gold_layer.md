# Gold Layer (Analytics & Reporting Layer)

## Overview

The Gold Layer represents the **analytics-facing surface** of the N-AIRS data platform.  
It is a curated, stable set of **fact and dimension objects** designed exclusively for BI tools such as Power BI.

This layer abstracts internal pipeline complexity and exposes a **schema-stable analytics contract** that supports:

- Business reporting
- Decision analysis
- Performance tracking
- Data quality monitoring

**Power BI connects only to this layer** and never directly to raw or intermediate pipeline tables.

---

## Why a Gold Layer Exists

Directly connecting BI tools to raw or pipeline tables introduces several risks:

- Schema changes break dashboards
- Business logic is duplicated in BI
- Data quality issues propagate to visuals
- Tight coupling between ingestion and reporting
- Poor onboarding experience for analysts

The Gold Layer resolves these by acting as a **semantic boundary** between data engineering and analytics.

**Design Principle:**  
*Internal tables may evolve. Gold Layer schemas must remain backward compatible.*

---

## Layering Model

N-AIRS follows a simplified **medallion-style architecture**:

| Layer  | Description                                   | BI Access |
|--------|-----------------------------------------------|-----------|
| Bronze | Raw ingested market data                      | ❌        |
| Silver | Processed, validated, feature-enriched data   | ❌        |
| Gold   | Analytics-ready fact & dimension objects      | ✅        |

---

## Gold Layer Objects

The current Gold Layer consists of **four objects**:

| Object               | Type  | Purpose                                              |
|----------------------|-------|------------------------------------------------------|
| `fact_signals`       | VIEW  | Central fact table representing trade signals and outcomes |
| `dim_calendar`       | TABLE | Date dimension for time intelligence                 |
| `dim_stocks`         | VIEW  | Stock symbol dimension                               |
| `rpt_quality_summary`| VIEW  | Aggregated data quality metrics                      |

---

## Object Definitions

### 1. **fact_signals** (Fact View)

**Grain:**  
One row per signal per stock per trading day

**Purpose:**  
Supports signal analysis, performance measurement, and decision explainability.

**Source Tables:**
- `decisions`
- `raw_prices_signal_outcomes`

**Key Columns:**

| Column            | Description                      |
|-------------------|----------------------------------|
| `decision_id`     | Unique signal identifier         |
| `trade_date`      | Signal date                      |
| `stock_symbol`    | Equity identifier                |
| `action`          | BUY / SELL / HOLD                |
| `confidence_score`| Model confidence                 |
| `reason_code`     | Rule or indicator trigger        |
| `return_5d`       | 5-day post-signal return         |
| `return_10d`      | 10-day post-signal return        |
| `outcome_label`   | WIN / LOSS / NEUTRAL             |

This view establishes the **decision → outcome feedback loop**, which is central to N-AIRS.

---

### 2. **dim_calendar** (Date Dimension)

**Type:** Physical table  
**Purpose:** Enables time-based analysis in Power BI (MoM, YoY, trends)

**Key Columns:**

| Column         | Description         |
|----------------|---------------------|
| `date_key`     | Primary date        |
| `year`         | Calendar year       |
| `quarter`      | Calendar quarter    |
| `month`        | Month number        |
| `month_name`   | Month name          |
| `week_of_year` | ISO week            |
| `weekday_name` | Day name            |

This table is populated from existing market data and maintained independently of BI.

---

### 3. **dim_stocks** (Stock Dimension)

**Type:** View  
**Purpose:** Provides a stable dimension for filtering and grouping.

**Grain:** One row per stock symbol

**Current Columns:**
- `stock_symbol`

This dimension can be extended later with:
- Company name
- Sector
- Market capitalization

---

### 4. **rpt_quality_summary** (Data Quality Reporting View)

**Purpose:**  
Provides transparency into data quality and pipeline reliability.

**Source Table:**
- `data_quality_raw_metrics`

**Metrics Included:**

| Metric               | Description                        |
|----------------------|------------------------------------|
| `anomaly_count`      | Number of detected anomalies       |
| `avg_missing_pct`    | Average missing data percentage    |
| `avg_price_zscore`   | Average price anomaly score        |
| `avg_volume_zscore`  | Average volume anomaly score       |

This view allows dashboards to answer:  
*"Can today's signals be trusted?"*

---

## Power BI Consumption Guidelines

**Power BI must connect only to the Gold Layer objects:**

- `fact_signals`
- `dim_calendar`
- `dim_stocks`
- `rpt_quality_summary`

### Relationships (Star Schema)

| From                              | To                         |
|-----------------------------------|----------------------------|
| `fact_signals.trade_date`         | `dim_calendar.date_key`    |
| `fact_signals.stock_symbol`       | `dim_stocks.stock_symbol`  |
| `rpt_quality_summary.trade_date`  | `dim_calendar.date_key`    |
| `rpt_quality_summary.stock_symbol`| `dim_stocks.stock_symbol`  |

This forms a **clean star schema** optimized for analytical queries.

---

## Design Guarantees

The Gold Layer guarantees:

- ✅ Stable column names and data types
- ✅ No destructive operations
- ✅ Business logic centralized upstream
- ✅ BI-friendly grain and relationships
- ✅ Backward compatibility across pipeline changes

---

## Future Extensions

Planned enhancements to the Gold Layer include:

- Index benchmark fact (`fact_index_benchmark`)
- Sector and asset metadata dimensions
- Pre-aggregated performance snapshots
- Materialized views for performance scaling

These will be introduced **without breaking existing dashboards**.

---

## Summary

The Gold Layer is the **analytics contract** of N-AIRS.

It decouples:

- Engineering evolution from reporting stability
- Raw data complexity from business insight
- Pipeline operations from visualization logic

This approach aligns with production data platforms used in large-scale analytics environments.
