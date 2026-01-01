import pandas as pd
import mysql.connector
import yaml
from datetime import datetime
import os
import ta
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

cursor = con.cursor()

# Fetch data
query_index = "SELECT index_name AS symbol, trade_date, close_price FROM index_prices ORDER BY trade_date"
query_stocks = "SELECT stock_symbol AS symbol, trade_date, close_price FROM raw_prices ORDER BY trade_date"

df_index = pd.read_sql(query_index, con)
df_stocks = pd.read_sql(query_stocks, con)

# Combine & preprocess
df_all = pd.concat([df_index, df_stocks], ignore_index=True)
df_all['trade_date'] = pd.to_datetime(df_all['trade_date'])
df_all = df_all.sort_values(by=['symbol', 'trade_date'])

# Indicator calculation per symbol
def calculate_technical_indicators(group):
    g = group.copy()
    g['rsi_14'] = ta.momentum.rsi(g['close_price'], window=14)
    macd = ta.trend.MACD(g['close_price'])
    g['macd'] = macd.macd()
    g['macd_signal'] = macd.macd_signal()
    g['momentum_10d'] = ta.momentum.roc(g['close_price'], window=10)
    g['volatility_20d'] = ta.volatility.bollinger_hband_indicator(g['close_price'], window=20)
    g['sma_20'] = ta.trend.sma_indicator(g['close_price'], window=20)
    g['ema_50'] = ta.trend.ema_indicator(g['close_price'], window=50)
    return g

df_indicators = (
    df_all.groupby('symbol', group_keys=False)
          .apply(calculate_technical_indicators)
          .reset_index(drop=True)
)

# Prepare batch insert
insert_query = """
INSERT INTO features
(stock_symbol, trade_date, rsi_14, macd, macd_signal, momentum_10d,
 volatility_20d, sma_20, ema_50, feature_run_id)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

run_id = f"techind_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
batch_data = []

for _, row in df_indicators.iterrows():
    batch_data.append((
        row['symbol'],
        row['trade_date'].date(),
        float(row['rsi_14']) if pd.notna(row['rsi_14']) else None,
        float(row['macd']) if pd.notna(row['macd']) else None,
        float(row['macd_signal']) if pd.notna(row['macd_signal']) else None,
        float(row['momentum_10d']) if pd.notna(row['momentum_10d']) else None,
        float(row['volatility_20d']) if pd.notna(row['volatility_20d']) else None,
        float(row['sma_20']) if pd.notna(row['sma_20']) else None,
        float(row['ema_50']) if pd.notna(row['ema_50']) else None,
        run_id
    ))

# Execute in batches
cursor.executemany(insert_query, batch_data)
con.commit()

cursor.close()
con.close()

print("Indicators processed and inserted successfully.")
print(f"Run ID: {run_id}")
