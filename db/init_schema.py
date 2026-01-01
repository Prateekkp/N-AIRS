import mysql.connector
import yaml
import os

# load configurations
with open('../config/config.yml', 'r') as file:
    config = yaml.safe_load(file)

db_info = config['mysql']

# connect to the database
connection = mysql.connector.connect(
    host=db_info['host'],
    user=db_info['user'],
    password=db_info['password'],
    database= db_info['database']
)

cursor = connection.cursor()

# Read schema file
schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'table-schema.sql')

with open(schema_path, 'r', encoding='utf-8') as sql_file:
    schema_commands = sql_file.read()

# Run commands
for command in schema_commands.split(";"):
    cmd = command.strip()
    if cmd:
        cursor.execute(cmd)

# Mark System Initialization Status
cursor.execute("""
INSERT INTO system_metadata (id, is_initialized)
VALUES (1, 1)
ON DUPLICATE KEY UPDATE
    is_initialized = 1,
    last_initialized = CURRENT_TIMESTAMP;
""")

connection.commit()

print("Database schema initialized. All tables are set up.")

cursor.close()
connection.close()