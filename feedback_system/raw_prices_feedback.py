import mysql.connector
import yaml
import os
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load configuration
with open('../config/config.yml', 'r') as file:
    config = yaml.safe_load(file)

con = mysql.connector.connect(
    host=config["mysql"]["host"],
    user=config["mysql"]["user"],
    password=config["mysql"]["password"],
    database=config["mysql"]["database"]
)

# ======================================
# FETCH from raw_prices
# ======================================
query = """
SELECT stock_symbol, trade_date, close_price
FROM raw_prices
ORDER BY stock_symbol, trade_date;
"""

df = pd.read_sql(query, con)
df['trade_date'] = pd.to_datetime(df['trade_date'])

# ======================================
# CALCULATE PERFORMANCE METRICS
# ======================================
df['return_5d'] = df.groupby('stock_symbol')['close_price'].pct_change(5)
df['return_10d'] = df.groupby('stock_symbol')['close_price'].pct_change(10)
df['max_drawdown'] = df.groupby('stock_symbol')['close_price'].transform(
    lambda x: (x - x.rolling(10, min_periods=1).min()) / x * 100
)


# ======================================
# ACTION COLUMN (initial default)
# Replace this later with your SIGNAL ENGINE output
# ======================================
df['action'] = "BUY"

# ======================================
# OUTCOME LOGIC
# ======================================
def evaluate_outcome(action, r):
    if pd.isna(r):
        return None, None

    # HIT or MISS
    outcome = "MISS"
    if action == "BUY" and r > 0:
        outcome = "HIT"
    elif action == "SELL" and r < 0:
        outcome = "HIT"
    elif action in ["WATCH", "HOLD"]:
        outcome = "HIT"

    # magnitude/strength label (optional but production useful)
    if r > 0.01:
        magnitude = "STRONG_WIN"
    elif 0 < r <= 0.01:
        magnitude = "WEAK_WIN"
    elif r < -0.01:
        magnitude = "STRONG_LOSS"
    elif -0.01 <= r < 0:
        magnitude = "WEAK_LOSS"
    else:
        magnitude = None

    return outcome, magnitude


df[['outcome_label', 'magnitude_label']] = df.apply(
    lambda row: evaluate_outcome(row['action'], row['return_5d']),
    axis=1,
    result_type="expand"
)

final_df = df.rename(columns={"trade_date": "signal_date"})

# ======================================
# BATCH INSERT
# ======================================
insert_query = """
INSERT INTO raw_prices_signal_outcomes
(stock_symbol, signal_date, action, return_5d, return_10d, max_drawdown, outcome_label)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

cur = con.cursor(buffered=True)

batch_records = [
    (
        row['stock_symbol'],
        row['signal_date'].date(),
        row['action'],
        float(row['return_5d']) if pd.notna(row['return_5d']) else None,
        float(row['return_10d']) if pd.notna(row['return_10d']) else None,
        float(row['max_drawdown']) if pd.notna(row['max_drawdown']) else None,
        row['outcome_label']
    )
    for _, row in final_df.iterrows()
]

if batch_records:
    cur.executemany(insert_query, batch_records)
    con.commit()
    print(f"INSERTED ROWS: {cur.rowcount}")
else:
    print("No data to insert, verify source table.")

cur.close()
con.close()

print("Data inserted into raw_prices_signal_outcomes successfully.")
