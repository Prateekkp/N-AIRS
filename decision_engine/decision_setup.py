import yaml
import uuid
import mysql.connector
import pandas as pd
import os
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

from rules import apply_rules
from scorer import decide
from writer import batch_write_decisions, close_connection

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load main DB config
with open('../config/config.yml', 'r') as file:
    cfg_db = yaml.safe_load(file)


def fetch_features():
    con = mysql.connector.connect(
        host=cfg_db["mysql"]["host"],
        user=cfg_db["mysql"]["user"],
        password=cfg_db["mysql"]["password"],
        database=cfg_db["mysql"]["database"]
    )

    query = """
    SELECT stock_symbol, trade_date, rsi_14, macd, macd_signal
    FROM features
    WHERE rsi_14 IS NOT NULL 
      AND macd IS NOT NULL 
      AND macd_signal IS NOT NULL
    ORDER BY trade_date;
    """

    df = pd.read_sql(query, con)
    con.close()
    return df


def run_engine(batch_size=5000):
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")
    cfg = yaml.safe_load(open(cfg_path))
    df = fetch_features()
    run_id = "run_" + uuid.uuid4().hex

    decisions_batch = []

    try:
        for _, row in df.iterrows():
            score, reasons = apply_rules(row, cfg)
            action, confidence, reasons = decide(score, reasons, cfg)

            decisions_batch.append((
                str(uuid.uuid4()),
                run_id,
                row["trade_date"],
                row["stock_symbol"],
                action,
                confidence,
                ",".join(reasons),
                datetime.now()
            ))

            if len(decisions_batch) >= batch_size:
                batch_write_decisions(decisions_batch)
                decisions_batch.clear()

        if decisions_batch:
            batch_write_decisions(decisions_batch)

        print(f"Decision Engine completed. Run ID: {run_id}")
    finally:
        close_connection()


if __name__ == "__main__":
    run_engine()
