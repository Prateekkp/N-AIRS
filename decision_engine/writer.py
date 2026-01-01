import mysql.connector
import yaml
import os

# Load DB config using absolute path relative to this file
cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'config.yml')
with open(cfg_path, 'r') as file:
    db_cfg = yaml.safe_load(file)

connection = None
cursor = None

def _ensure_connection():
    global connection, cursor
    if connection is None or not connection.is_connected():
        connection = mysql.connector.connect(
            host=db_cfg["mysql"]["host"],
            user=db_cfg["mysql"]["user"],
            password=db_cfg["mysql"]["password"],
            database=db_cfg["mysql"]["database"]
        )
        cursor = connection.cursor()

INSERT_QUERY = """
INSERT INTO decisions
(decision_id, run_id, trade_date, stock_symbol, action, confidence_score, reason_code, created_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

def batch_write_decisions(records):
    _ensure_connection()
    cursor.executemany(INSERT_QUERY, records)
    connection.commit()

def close_connection():
    global connection, cursor
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()
    cursor = None
    connection = None
