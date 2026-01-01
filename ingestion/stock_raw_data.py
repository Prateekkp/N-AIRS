import pandas as pd
import yfinance as yf
import yaml, uuid, mysql.connector
from datetime import datetime
import os
import warnings
warnings.filterwarnings("ignore")

# move to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ============ Load configuration ============
with open('../config/config.yml', 'r') as file:
    config = yaml.safe_load(file)

start_date = config["market_data"]["start_date"]
end_date = datetime.today().strftime('%Y-%m-%d') if config["market_data"]["end_date"].lower() == 'today' else config["market_data"]["end_date"]
interval = config["market_data"]["interval"]
url = config["url"]["company_list"]

run_id = f"{config['ingestion']['run_id_stock_prefix']}_{uuid.uuid4().hex[:8]}"

df_list = pd.read_csv(url)
symbols = df_list['Symbol'].tolist()
tickers = [s + ".NS" for s in symbols]

print("\nFetching ALL valid NSE symbols...")
data = yf.download(
    tickers,
    start=start_date,
    end=end_date,
    interval=interval,
    group_by="ticker",
    auto_adjust=False,
    threads=True,
    progress=False
)

con = mysql.connector.connect(
    host=config["mysql"]["host"],
    user=config["mysql"]["user"],
    password=config["mysql"]["password"],
    database=config["mysql"]["database"]
)
cursor = con.cursor()

# log ingestion start time
start_time = datetime.now()
cursor.execute("""
INSERT INTO ingestion_logs (run_id, pipeline_type, start_time, status)
VALUES (%s, %s, %s, %s)
""", (run_id, "stock", start_time, "RUNNING"))
con.commit()

query = """
INSERT IGNORE INTO raw_prices
(stock_symbol, trade_date, open_price, high_price, low_price, close_price, volume, run_id)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

rows_to_insert = []
print("\nPreparing batch insert...")

# If multi-index → use columns as (symbol, field)
if isinstance(data.columns, pd.MultiIndex):
    for symbol in symbols:
        symbol_ns = symbol + ".NS"
        try:
            stock_df = data[symbol_ns].dropna()
        except KeyError:
            print(f"⚠️ {symbol_ns}: Not found on Yahoo. Skipping.")
            continue

        for date, row in stock_df.iterrows():
            rows_to_insert.append((
                symbol,
                date.date(),
                float(row["Open"]),
                float(row["High"]),
                float(row["Low"]),
                float(row["Close"]),
                int(row["Volume"]),
                run_id
            ))

# If single index (fallback)
else:
    print("Fallback single-ticker structure encountered.")
    for date, row in data.dropna().iterrows():
        ticker = "UNKNOWN"
        rows_to_insert.append((
            ticker,
            date.date(),
            float(row["Open"]),
            float(row["High"]),
            float(row["Low"]),
            float(row["Close"]),
            int(row["Volume"]),
            run_id
        ))

# log ingestion end time
end_time = datetime.now()
cursor.execute("""
    UPDATE ingestion_logs
    SET end_time=%s, status=%s, records_loaded=%s
    WHERE run_id=%s
    """, 
    (end_time, "SUCCESS", len(rows_to_insert), run_id))

cursor.executemany(query, rows_to_insert)
con.commit()
cursor.close()
con.close()

print(f"Mission Complete — {len(rows_to_insert)} rows ingested.")
print(f"Run ID: {run_id}")