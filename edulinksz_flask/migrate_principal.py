import sqlite3
import os

def migrate_db():
    db_path = os.path.join('instance', 'edulinksz.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # SchoolProfile columns
        try:
            c.execute("ALTER TABLE school_profile ADD COLUMN email VARCHAR(150)")
            print("Added email to school_profile")
        except sqlite3.OperationalError:
            print("email already exists")
            
        try:
            c.execute("ALTER TABLE school_profile ADD COLUMN tel VARCHAR(50)")
            print("Added tel to school_profile")
        except sqlite3.OperationalError:
            print("tel already exists")
            
        try:
            c.execute("ALTER TABLE school_profile ADD COLUMN phone VARCHAR(50)")
            print("Added phone to school_profile")
        except sqlite3.OperationalError:
            print("phone already exists")
            
        # TermReport columns
        try:
            c.execute("ALTER TABLE term_report ADD COLUMN is_approved BOOLEAN DEFAULT 0")
            print("Added is_approved to term_report")
        except sqlite3.OperationalError:
            print("is_approved already exists")
            
        conn.commit()
        conn.close()
        print("Migration complete.")
    else:
        print(f"Database {db_path} not found. Migration skipped.")

if __name__ == '__main__':
    migrate_db()
