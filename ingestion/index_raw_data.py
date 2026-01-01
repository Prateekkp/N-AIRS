import yfinance as yf
import yaml
import uuid
import mysql.connector
from datetime import datetime
import os
import warnings
warnings.filterwarnings("ignore")

# move to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# load the configuration file
with open('../config/config.yml', 'r') as file:
    config = yaml.safe_load(file)

symbol = config["market_data"]["index_symbol"]
index_name = config["market_data"]["index_name"]
start_date = config["market_data"]["start_date"]
end_date = config["market_data"]["end_date"]
interval = config["market_data"]["interval"]

# convert end_date to datetime object
if end_date.lower() == 'today':
    end_date = datetime.today().strftime('%Y-%m-%d')
else:
    end_date = end_date

# generate run_id 
run_id = f"{config['ingestion']['run_id_nifty_prefix']}_{uuid.uuid4().hex[:8]}"


# Fetch data from yfinance
df = yf.download(symbol, start=start_date, end=end_date, interval=interval)

# prepare mysql connection
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
""", (run_id, "index", start_time, "RUNNING"))
con.commit()

# insert query
query = """
INSERT IGNORE INTO index_prices
(index_name, trade_date, open_price, high_price, low_price, close_price, volume, run_id)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""


# iterate row and insert
for trade_date, row in df.iterrows():
    payload = (
        index_name,
        trade_date.date(),
        round(float(row["Open"]), 2),
        round(float(row["High"]), 2),
        round(float(row["Low"]), 2),
        round(float(row["Close"]), 2),
        int(row["Volume"]) if not str(row["Volume"]) == 'nan' else None,
        run_id
    )
    cursor.execute(query, payload)

# log ingestion end time
end_time = datetime.now()
cursor.execute("""
    UPDATE ingestion_logs
    SET end_time=%s, status=%s, records_loaded=%s
    WHERE run_id=%s
    """, 
    (end_time, "SUCCESS", len(df), run_id))

con.commit()
cursor.close()
con.close()