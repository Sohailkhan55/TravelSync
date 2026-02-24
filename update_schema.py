from database.db_manager import get_connection

def migrate():
    print("Migrating database...")
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE groups ADD COLUMN destination TEXT")
        print("Success: Added 'destination' column.")
    except Exception as e:
        print(f"Notice: {e} ('destination' might already exist)")
        
    try:
        c.execute("ALTER TABLE groups ADD COLUMN insider_data TEXT")
        print("Success: Added 'insider_data' column.")
    except Exception as e:
        print(f"Notice: {e} ('insider_data' might already exist)")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
