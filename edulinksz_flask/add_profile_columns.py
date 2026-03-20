import sqlite3
import os

def migrate_db():
    db_path = os.path.join('instance', 'edulinksz.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        try:
            c.execute("ALTER TABLE school_profile ADD COLUMN letterhead_url VARCHAR(255)")
            print("Added letterhead_url to school_profile")
        except sqlite3.OperationalError as e:
            print(f"Adding letterhead_url: {e}")

        try:
            c.execute("ALTER TABLE school_profile ADD COLUMN signature_url VARCHAR(255)")
            print("Added signature_url to school_profile")
        except sqlite3.OperationalError as e:
            print(f"Adding signature_url: {e}")
            
        conn.commit()
        conn.close()
        print("Migration complete.")
    else:
        print(f"Database {db_path} not found. Migration skipped.")

if __name__ == '__main__':
    migrate_db()
