import mysql.connector
import yaml
import os
import pandas as pd
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

# ======================================
# FETCH INDEX DATA
# ======================================
query = """
SELECT index_name AS index_symbol, trade_date, close_price
FROM index_prices
WHERE REPLACE(index_name,' ','') = 'NIFTY50'
ORDER BY trade_date;
"""

df = pd.read_sql(query, con)
df['trade_date'] = pd.to_datetime(df['trade_date'])

# ======================================
# CALCULATIONS
# ======================================
df['return_5d'] = df['close_price'].pct_change(5)
df['return_10d'] = df['close_price'].pct_change(10)
df['max_drawdown'] = (
    df['close_price'] - df['close_price'].rolling(10, min_periods=1).min()
) / df['close_price'] * 100

# Placeholder action (to replace with signal logic later)
df['action'] = "BUY"

# ======================================
# OUTCOME LOGIC
# ======================================
def evaluate_outcome(action, r):
    if pd.isna(r):
        return None, None
    
    # HIT / MISS
    outcome = "MISS"
    if action == "BUY" and r > 0:
        outcome = "HIT"
    elif action == "SELL" and r < 0:
        outcome = "HIT"
    elif action in ["WATCH", "HOLD"]:
        outcome = "HIT"
    
    # STRENGTH / GRADE
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

# ======================================
# FINAL FORMAT
# ======================================
final_df = df.rename(columns={"trade_date": "signal_date"})

# ======================================
# INSERT INTO index_prices_signal_outcomes
# ======================================
insert_query = """
INSERT INTO index_prices_signal_outcomes
(index_symbol, signal_date, action, return_5d, return_10d, max_drawdown, outcome_label)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

cur = con.cursor(buffered=True)

batch_data = [
    (
        row['index_symbol'],
        row['signal_date'].date(),
        row['action'],
        float(row['return_5d']) if pd.notna(row['return_5d']) else None,
        float(row['return_10d']) if pd.notna(row['return_10d']) else None,
        float(row['max_drawdown']) if pd.notna(row['max_drawdown']) else None,
        row['outcome_label']
    )
    for _, row in final_df.iterrows()
]

if batch_data:
    cur.executemany(insert_query, batch_data)
    con.commit()
    print(f"INSERTED ROWS: {cur.rowcount} rows recorded in index_prices_signal_outcomes.")
else:
    print("No data to insert. Please check source table.")

cur.close()
con.close()

print("Mission Complete — Outcomes Stored Successfully.")
