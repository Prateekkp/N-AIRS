# **N-AIRS**

**Automated Market Intelligence & Rule-Based Decision Engine**

![Python](https://img.shields.io/badge/Python-3.10+-yellow?logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/DB-MySQL-4479A1?logo=mysql&logoColor=white)
![Status](https://img.shields.io/badge/Build-Under_Development-blue)
![Architecture](https://img.shields.io/badge/Design-Modular-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)


> **Status:** Pre-Production • Modular Architecture • Scalable for Cloud & CI/CD Integration  
> **Owner:** Prateek Kumar Prasad

---

## **Overview**

N-AIRS is a modular financial analytics system designed to automate market data ingestion, feature computation, signal generation, and outcome tracking.
The architecture emphasizes **separation of concerns**, **configuration-driven behavior**, **database-backed state**, and **production scalability**.

The objective is to create a system that can be integrated into:

* Quantitative trading strategies
* Market analysis platforms
* Signal intelligence dashboards
* Automated research systems

---

## **Architecture**

```mermaid
graph TD
  A["Market Data APIs"] -->|Raw Feeds| B["Ingestion Layer"]
  B -->|Indexed & Raw Data| C["Quality Gate"]
  C -->|Validated Data| D["Feature Store"]
  D -->|Technical Indicators| E["Decision Engine"]
  E -->|Buy/Sell/Hold Signals| F["Feedback System"]
  F -->|Outcome Tracking| G["MySQL Data Store"]
  G -->|Reporting Views| H["Gold Layer"]
  H -->|Star Schema| I["Power BI Dashboard"]
    
  C -->|Anomaly Alerts| G
  D -->|Computed Features| G
  E -->|Decision Rules| G
    
  style A fill:#e1f5ff
  style B fill:#fff3e0
  style C fill:#fce4ec
  style D fill:#f3e5f5
  style E fill:#e8f5e9
  style F fill:#fff9c4
  style G fill:#eceff1
  style H fill:#dcedc8
  style I fill:#bbdefb
```

---

## **Key Capabilities**

| Module          | Description                                                      |
| --------------- | ---------------------------------------------------------------- |
| **Ingestion**   | Fetches and stores index & equity data at defined intervals      |
| **Quality Gate** | Schema validation, anomaly detection, and data integrity metrics |
| **Feature Store** | Computes technical indicators & engineered variables             |
| **Decision Engine** | YAML-driven rule evaluation for BUY/SELL/HOLD outcomes           |
| **Feedback System** | Tracks realized outcomes for reinforcement & strategy review     |

---

## **Project Structure**

```
N-AIRS/
 ├── config/              # Environment & DB configuration
 ├── db/                  # Schema, migrations, setup scripts
 ├── ingestion/           # Data fetchers, loaders
 ├── quality_gate/        # Validation & anomaly detection
 ├── feature_store/       # Technical indicators & features
 ├── decision_engine/     # Rule processing & signal generation
 ├── feedback_system/     # Outcome capture & learning
 ├── run_pipeline.py      # Unified pipeline entrypoint
 ├── requirements.txt     # Dependencies
 └── README.md            # Project documentation
```

---

## **Data Flow (Detailed)**

```mermaid
sequenceDiagram
    participant API as Market APIs
    participant ING as Ingestion
    participant QG as Quality Gate
    participant FS as Feature Store
    participant DE as Decision Engine
    participant DB as MySQL
    participant FB as Feedback System

    API->>ING: Raw Market Data
    ING->>DB: Store Raw Data
    ING->>QG: Pass Data
    
    QG->>QG: Validate Schema
    QG->>QG: Detect Anomalies
    QG->>DB: Store Validation Results
    QG->>FS: Validated Data
    
    FS->>FS: Compute Indicators
    FS->>DB: Store Features
    FS->>DE: Feature Set
    
    DE->>DE: Evaluate Rules
    DE->>DB: Store Signals
    DE->>FB: Decision Output
    
    FB->>FB: Track Outcomes
    FB->>DB: Store Feedback
    FB->>DE: Learning Insights
```

---

## **Environment Setup**

### **Prerequisites**

* Python **3.10+**
* MySQL **8+**
* Git

### **Installation**

```bash
git clone https://github.com/prateekkp/N-AIRS.git
cd N-AIRS
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

## **Configuration**

#### **config.yml**

```yaml
mysql:
  host: "" # e.g., "localhost" 
  user: "" # e.g., "root"
  password: "" # e.g., "password"
  database: "NAIRS"

market_data:
  index_symbol: "^NSEI"
  index_name: "NIFTY 50"
  start_date: "2020-01-01"
  end_date: "today"
  interval: "1d"

ingestion:
  run_id_nifty_prefix: "NIFTY_INGEST"
  run_id_stock_prefix: "STOCK_INGEST"

url:
  company_list: "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
```

⚠️ **Security**: Do **not** commit actual credentials.  


---



## **Pipeline Execution**

### **Full Pipeline**

```bash
python run_pipeline.py
```

- Gold Layer publish: the pipeline now executes [db/gold-layer-schema.sql](db/gold-layer-schema.sql) as the final step to materialize the reporting views (`fact_signals`, `dim_calendar`, `dim_stocks`, `rpt_quality_summary`) consumed by Power BI.

### **Individual Module Execution**

```bash
# Database Setup
python db/setup_db.py

# Ingestion only
python ingestion/ingest_setup.py

# Quality checks
python quality_gate/quality_setup.py

# Feature computation
python feature_store/technical_indicator.py

# Decision generation
python decision_engine/decision_setup.py

# Feedback capture
python feedback_system/feedback_setup.py
```

---

## **Artifacts & Outputs**
- Power BI report: [artifacts/dashboard/nairs_decision_engine.pbix](artifacts/dashboard/nairs_decision_engine.pbix)
- Dashboard preview (PNG): [artifacts/outputs/nairs_decision_engine.png](artifacts/outputs/nairs_decision_engine.png)
- Recent terminal run log (screenshot): [artifacts/outputs/Terminal-Execution.png](artifacts/outputs/Terminal-Execution.png)

**Previews**

![Power BI Dashboard Preview](artifacts/outputs/nairs_decision_engine.png)

![Terminal Execution Log](artifacts/outputs/Terminal-Execution.png)

---

## **Module Reference**

### **Ingestion Layer**
- `stock_raw_data.py` — Fetches equity prices
- `index_raw_data.py` — Fetches index prices
- `ingest_setup.py` — Initializes data fetchers

### **Quality Gate**
- `schema_validation.py` — Validates data structure
- `anomaly_detection_raw.py` — Detects outliers in raw data
- `anomaly_detection_index.py` — Detects index anomalies
- `quality_setup.py` — Configures thresholds

### **Feature Store**
- `technical_indicator.py` — Computes RSI, MACD, Bollinger Bands, etc.

### **Decision Engine**
- `rules.py` — Defines trading rules
- `scorer.py` — Evaluates signals against rules
- `writer.py` — Writes decisions to database
- `config.yml` — YAML-based rule definitions

### **Reporting Layer**
- Gold Layer contract: [docs/gold_layer.md](docs/gold_layer.md)
- Power BI dashboard spec: [docs/powerbi_dashboard.md](docs/powerbi_dashboard.md)

### **Feedback System**
- `raw_prices_feedback.py` — Tracks outcome vs. prediction (raw data)
- `index_prices_feedback.py` — Tracks outcome vs. prediction (index data)
- `feedback_setup.py` — Initializes feedback system

---

## **Performance & Monitoring**

### **Expected Metrics**

* Ingestion: ~500 records/min per worker
* Quality Gate: ~10ms per record validation
* Feature Computation: ~5ms per indicator per record
* Decision Evaluation: <1ms per rule per signal

### **Observability Stack**

```mermaid
graph LR
    A["N-AIRS Process"] -->|Logs| B["Log Aggregator"]
    A -->|Metrics| C["Prometheus"]
    B --> D["Grafana Dashboard"]
    C --> D
    A -->|Traces| E["Jaeger"]
```

---

## **Troubleshooting**

| Issue | Solution |
| --- | --- |
| Database connection fails | Verify MySQL running, credentials correct, network access |
| Missing technical indicators | Check feature_store config, ensure sufficient historical data |
| Decision rules not firing | Validate YAML syntax in decision_engine/config.yml |
| Data anomalies flagged | Review quality_gate thresholds, check source data quality |

---

## **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add feature description"`
4. Push to branch: `git push origin feature/your-feature`
5. Submit pull request

**Code review required before merge.**

---

## **License**

MIT License — Free for educational and research use.

See `LICENSE` file for full details.

---

## **Contact & Support**

**Maintainer:** Prateek Kumar Prasad  
**Email:** [prateekkumarprasad15@gmail.com](mailto:prateekkumarprasad15@gmail.com)  
**Status:** Active development  
**Last Updated:** January 2026

---

## **References**

- [Technical Analysis Indicators](https://en.wikipedia.org/wiki/Technical_analysis)
- [YAML Configuration Format](https://yaml.org/spec/1.2/spec.html)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Python Best Practices](https://pep8.org/)

---

> *Prepared with the precision of an operations briefing.*  
> *If it's not clear, it's not deployable.*  
> **Ready for deployment. Executing mission. 🫡**
