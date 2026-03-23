import sqlite3
import os

def migrate():
    db_path = os.path.join('instance', 'edulinksz.db')
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Add email column to user table
        cursor.execute("ALTER TABLE user ADD COLUMN email VARCHAR(150)")
        print("Added email column to user table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("email column already exists in user table.")
        else:
            print(f"Error adding email: {e}")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
