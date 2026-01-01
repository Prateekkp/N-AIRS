import os
import subprocess
import sys

# move to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("\nStarting Data Ingestion Process...\n")

def run_step(label, command):
    print(f"{label} ...")
    try:
        subprocess.run(command, check=True)
        print(f" {label} completed.\n")
    except subprocess.CalledProcessError:
        print(f" {label} FAILED. Aborting ingestion.\n")
        sys.exit(1)

# execute ingestion scripts in order
run_step("Index Price Ingestion", ["python", "index_raw_data.py"])
run_step("Stock Price Ingestion", ["python", "stock_raw_data.py"])

print("Data Ingestion completed successfully.\n")
