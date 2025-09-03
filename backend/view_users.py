import sqlite3
import os

# Get the path of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Full path to users.db
DB_PATH = os.path.join(BASE_DIR, "users.db")

# Connect to the database
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Fetch all users
cur.execute("SELECT * FROM users")
rows = cur.fetchall()

for row in rows:
    print(dict(row))

conn.close()
