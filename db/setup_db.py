import subprocess
import os
import mysql.connector
import yaml
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Detect if running standalone or from pipeline
VERBOSE = "--verbose" in sys.argv

def log(msg):
    if VERBOSE:
        print(msg)

log("Initializing N-AIRS Database Setup...")

with open('../config/config.yml', 'r') as file:
    config = yaml.safe_load(file)['mysql']


def run_cmd(label, command):
    try:
        log(f"{label} ...")
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log(f"{label} completed.")
    except subprocess.CalledProcessError:
        print(f"{label} FAILED.")
        sys.exit(1)


# 1) Ensure DB exists
run_cmd("Creating database", ["python", "create_db.py"])


# 2) Check metadata / initialization status
try:
    connection = mysql.connector.connect(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )
    cursor = connection.cursor()

    cursor.execute("SHOW TABLES LIKE 'system_metadata';")
    exists = cursor.fetchone()

    if exists:
        cursor.execute("SELECT is_initialized FROM system_metadata WHERE id = 1;")
        state = cursor.fetchone()

        if state and state[0] == 1:
            log("Database already initialized → Skipping schema setup.")
            cursor.close(); connection.close()
            sys.exit(0)

    log("Database not initialized, proceeding...")
    cursor.close(); connection.close()

except Exception as e:
    log(f"Metadata check warning: {e}. Continuing...")


# 3) Initialize schema
run_cmd("Initializing schema", ["python", "init_schema.py"])

log("N-AIRS database setup completed successfully.")
sys.exit(0)
