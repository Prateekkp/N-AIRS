import os
import subprocess
import sys
import mysql.connector
import yaml
from datetime import datetime
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
python_exe = sys.executable

print("\nPIPELINE STARTED")
run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
print(f"RUN ID: {run_id}")
print("--------------------------------------------------")

# =====================================================
# STEP 1 — DATABASE SETUP (NO LOGGING UNTIL DB EXISTS)
# =====================================================
print("[DB_SETUP] Executing db/setup_db.py ...")
result = subprocess.run([python_exe, "db/setup_db.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if result.returncode != 0:
    print("[DB_SETUP] FAILED - Database not created. Terminating pipeline.")
    sys.exit(1)
print("[DB_SETUP] OK")

# =====================================================
# INIT DB CONNECTION FOR LOGGING
# =====================================================
with open('config/config.yml', 'r') as file:
    config = yaml.safe_load(file)

db = config["mysql"]

for attempt in range(3):
    try:
        con = mysql.connector.connect(
            host=db["host"],
            user=db["user"],
            password=db["password"],
            database=db["database"]
        )
        break
    except mysql.connector.Error:
        print("[SYSTEM] Database not reachable. Retrying...")
        time.sleep(2)
else:
    print("[SYSTEM] ERROR: Database connection failed after retries")
    sys.exit(1)

cur = con.cursor()

# =====================================================
# SYSTEM HEALTH LOG FUNCTION
# =====================================================
def log_health(stage, status, message):
    query = """
    INSERT INTO system_health_snapshot (run_id, pipeline_stage, status, message)
    VALUES (%s, %s, %s, %s)
    """
    cur.execute(query, (run_id, stage, status, message))
    con.commit()

# =====================================================
# STEP EXECUTION HANDLER
# =====================================================
def run_step(file, label, stage_key):
    print(f"[{stage_key}] Executing {file} ...")
    result = subprocess.run([python_exe, file], capture_output=True, text=True)

    if result.returncode != 0:
        log_health(stage_key, "FAILED", result.stderr.strip() or "No stderr message")
        print(f"[{stage_key}] FAILED")
        cur.close()
        con.close()
        sys.exit(1)

    warning_msg = result.stderr.strip()
    if warning_msg:
        log_health(stage_key, "WARNING", warning_msg)
        print(f"[{stage_key}] COMPLETED WITH WARNINGS")
    else:
        log_health(stage_key, "OK", "Completed successfully")
        print(f"[{stage_key}] OK")

# =====================================================
# PIPELINE STEPS
# =====================================================
run_step("quality_gate/schema_validation.py",  "Schema Validation", "SCHEMA_VALIDATION")
run_step("ingestion/ingest_setup.py",          "Data Ingestion",    "INGESTION")
run_step("quality_gate/quality_setup.py",      "Quality Checks",    "QUALITY")
run_step("feature_store/technical_indicator.py","Technical Indicators","FEATURE_ENGINEERING")
run_step("decision_engine/decision_setup.py",  "Decision Engine",   "DECISION_ENGINE")
run_step("feedback_system/feedback_setup.py",  "Feedback Processing","FEEDBACK")

# =====================================================
# STEP: GOLD LAYER SCHEMA CREATION
# =====================================================
print("[GOLD_LAYER] Executing db/gold-layer-schema.sql ...")
try:
    with open('db/gold-layer-schema.sql', 'r') as f:
        sql_content = f.read()
    
    # Execute each statement separately
    for statement in sql_content.split(';'):
        statement = statement.strip()
        if statement:
            cur.execute(statement)
    
    con.commit()
    log_health("GOLD_LAYER", "OK", "Completed successfully")
    print("[GOLD_LAYER] OK")
except Exception as e:
    log_health("GOLD_LAYER", "FAILED", str(e))
    print("[GOLD_LAYER] FAILED")
    cur.close()
    con.close()
    sys.exit(1)

cur.close()
con.close()

print("--------------------------------------------------")
print("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
print(f"FINAL RUN ID: {run_id}")
print("--------------------------------------------------\n")
