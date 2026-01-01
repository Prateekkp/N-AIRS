import yaml
import mysql.connector

# load the configuration file
with open('../config/config.yml', 'r') as file:
    config = yaml.safe_load(file)

# extract the values
db_info = config['mysql']

# establish the database connection
connection = mysql.connector.connect(
    host=db_info['host'],
    user=db_info['user'],
    password=db_info['password']
)

print("Database connection established successfully.")

cursor = connection.cursor()

# Making a database if it doesn't exist
cursor.execute("CREATE DATABASE IF NOT EXISTS nairs")
print("Database 'nairs' ensured to exist.")

# close connection
cursor.close()
connection.close()