import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "travelsync.db")

def upgrade_chat_table():
    print(f"Upgrading DB at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Check if column exists
        c.execute("PRAGMA table_info(chat_messages)")
        cols = [col[1] for col in c.fetchall()]
        
        if "reply_to_id" not in cols:
            print("Adding reply_to_id column...")
            c.execute("ALTER TABLE chat_messages ADD COLUMN reply_to_id INTEGER DEFAULT NULL")
            conn.commit()
            print("Success.")
        else:
            print("Column reply_to_id already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_chat_table()
