import subprocess
import os
import sys

# Always move to project root (IMPORTANT)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_step(label, command):
    print(f"\n{label}...")
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"{label} FAILED. Aborting.\n")
        sys.exit(1)
    print(f"{label} completed.\n")

# Paths INSIDE the folder (relative from project root)
run_step("Index Anomaly Detection", ["python", "quality_gate/anomaly_detection_index.py"])
run_step("Raw Stocks Anomaly Detection", ["python", "quality_gate/anomaly_detection_raw.py"])

print("\nQuality checks completed successfully.\n")
