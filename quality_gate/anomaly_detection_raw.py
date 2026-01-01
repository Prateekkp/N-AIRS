import pandas as pd
import mysql.connector
import yaml
from datetime import datetime
import os
import warnings
warnings.filterwarnings("ignore")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load config
with open('../config/config.yml', 'r') as file:
    config = yaml.safe_load(file)

con = mysql.connector.connect(
    host=config["mysql"]["host"],
    user=config["mysql"]["user"],
    password=config["mysql"]["password"],
    database=config["mysql"]["database"]
)

# Fetch Data
df = pd.read_sql("SELECT * FROM raw_prices", con)

# Anomaly Detection
def detect_anomalies(df, threshold=3):
    close_z = (df['close_price'] - df['close_price'].mean()) / df['close_price'].std()
    volume_z = (df['volume'] - df['volume'].mean()) / df['volume'].std()

    df['price_zscore'] = close_z.round(4)
    df['volume_zscore'] = volume_z.round(4)
    df['is_anomalous'] = ((close_z.abs() > threshold) | (volume_z.abs() > threshold)).astype(int)
    return df

df = detect_anomalies(df)

# Prepare records for insertion
records = []
for _, row in df.iterrows():
    records.append((
        row['run_id'],
        row['stock_symbol'],
        row['trade_date'],
        0,
        row['price_zscore'],
        row['volume_zscore'],
        row['is_anomalous'],
        datetime.now()
    ))

cursor = con.cursor()

query = """
INSERT INTO data_quality_raw_metrics (
    run_id, stock_symbol, trade_date, missing_pct,
    price_zscore, volume_zscore, is_anomalous, checked_at
) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
"""

cursor.executemany(query, records)
con.commit()

cursor.close()
con.close()

print("Data Quality Metrics updated successfully.")
