# we need to validate schema of index_price and raw_data tables

import mysql.connector
import yaml
import os
import warnings
warnings.filterwarnings("ignore")

# move to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ============ Load Configuration ============
with open('../config/config.yml', 'r') as file:
    config = yaml.safe_load(file)

con = mysql.connector.connect(
    host=config["mysql"]["host"],
    user=config["mysql"]["user"],
    password=config["mysql"]["password"],
    database=config["mysql"]["database"]
)

cursor = con.cursor()

# Tables to check
table_names = ['index_prices', 'raw_prices']

# Required columns and expected base type
must_have_columns = {
    "trade_date": "date",
    "open_price": "decimal",
    "high_price": "decimal",
    "low_price": "decimal",
    "close_price": "decimal",
    "volume": "bigint"
}

print("\n============== SCHEMA VALIDATION REPORT ==============\n")

for table in table_names:
    cursor.execute(f"DESCRIBE {table}")
    columns = cursor.fetchall()
    
    db_columns = {col[0]: col[1].lower() for col in columns}  # dict → {column_name: datatype}

    missing_columns = []
    type_mismatches = []

    for col, expected_type in must_have_columns.items():

        if col not in db_columns:
            missing_columns.append(col)
        else:
            actual_type = db_columns[col]

            # check only the base type (example: "decimal(10,2)" → decimal)
            if not actual_type.startswith(expected_type.lower()):
                type_mismatches.append((col, expected_type, actual_type))
    
    print(f"Table: {table}")

    if missing_columns:
        print(f"Schema Validation Failed for table: {table}")
        print(f"   Missing Columns: {missing_columns}")
        print("   Aborting pipeline due to critical schema mismatch.\n")
        exit(1)

    if type_mismatches:
        print(f"Schema Validation Failed for table: {table}")
        print("Type Mismatches:")
        for col, exp, found in type_mismatches:
            print(f"      - {col}: expected {exp}, found {found}")
        print("Aborting pipeline due to incorrect column types.\n")
        exit(1)

    print("Schema validation passed for this table.")
    print("------------------------------------------------------")

print("\nAll checks completed.\n")

cursor.close()
con.close()
