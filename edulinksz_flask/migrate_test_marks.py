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
        # Add test1_marks column
        cursor.execute("ALTER TABLE result ADD COLUMN test1_marks FLOAT")
        print("Added test1_marks column to result table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("test1_marks column already exists.")
        else:
            print(f"Error adding test1_marks: {e}")

    try:
        # Add test2_marks column
        cursor.execute("ALTER TABLE result ADD COLUMN test2_marks FLOAT")
        print("Added test2_marks column to result table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("test2_marks column already exists.")
        else:
            print(f"Error adding test2_marks: {e}")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
