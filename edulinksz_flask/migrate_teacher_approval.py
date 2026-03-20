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
        # Add is_profile_approved column to user table
        # We use INTEGER (0/1) for Boolean in SQLite, default 1 (True)
        cursor.execute("ALTER TABLE user ADD COLUMN is_profile_approved BOOLEAN DEFAULT 1")
        print("Added is_profile_approved column to user table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("is_profile_approved column already exists in user table.")
        else:
            print(f"Error adding is_profile_approved: {e}")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
