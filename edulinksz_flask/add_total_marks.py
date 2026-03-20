import sqlite3
import os

def migrate_db():
    db_path = os.path.join('instance', 'edulinksz.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        try:
            c.execute("ALTER TABLE term_report ADD COLUMN total_marks FLOAT")
            print("Added total_marks to term_report")
        except sqlite3.OperationalError as e:
            print(f"Adding total_marks: {e}")
            
        conn.commit()
        conn.close()
        print("Migration complete.")
    else:
        print(f"Database {db_path} not found. Migration skipped.")

if __name__ == '__main__':
    migrate_db()
