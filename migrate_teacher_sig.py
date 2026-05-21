import sqlite3
import os

def migrate_db():
    db_path = os.path.join('instance', 'edulinksz.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # User columns
        try:
            c.execute("ALTER TABLE user ADD COLUMN signature_url VARCHAR(255)")
            print("Added signature_url to user")
        except sqlite3.OperationalError:
            print("signature_url already exists")
            
        conn.commit()
        conn.close()
        print("Migration complete.")
    else:
        print(f"Database {db_path} not found. Migration skipped.")

if __name__ == '__main__':
    migrate_db()
