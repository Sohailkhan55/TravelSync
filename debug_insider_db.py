from database.db_manager import get_connection

def  debug_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT group_id, group_name, destination, insider_data FROM groups")
    rows = c.fetchall()
    
    print(f"Found {len(rows)} groups.")
    for r in rows:
        print(f"ID: {r['group_id']}")
        print(f"Name: {r['group_name']}")
        print(f"Dest: {r['destination']}")
        data = r['insider_data']
        print(f"Insider Data Len: {len(data) if data else 0}")
        print(f"Insider Data Snippet: {data[:50] if data else 'None'}")
        print("-" * 20)
    conn.close()

if __name__ == "__main__":
    debug_db()
