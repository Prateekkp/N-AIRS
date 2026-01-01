import os
import subprocess
import sys

# move to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("\nStarting Feedback Processing...\n")

def run_step(label, command):
    print(f"{label} ...")
    try:
        subprocess.run(command, check=True)
        print(f" {label} completed.\n")
    except subprocess.CalledProcessError:
        print(f" {label} FAILED. Aborting ingestion.\n")
        sys.exit(1)

# execute ingestion scripts in order
run_step("Index Price Feedback Processing", ["python", "index_prices_feedback.py"])
run_step("Stock Price Feedback Processing", ["python", "raw_prices_feedback.py"])

print("Feedback Processing completed successfully.\n")