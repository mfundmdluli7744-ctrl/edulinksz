import sqlite3
import os

db_path = os.path.join('instance', 'edulinksz.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA table_info(school_profile);")
    columns = c.fetchall()
    for col in columns:
        print(col)
    conn.close()
else:
    print(f"Database {db_path} not found.")
