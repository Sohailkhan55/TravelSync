from database.db_manager import get_connection

conn = get_connection()
c = conn.cursor()
try:
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    print(f"Total Users: {len(users)}")
    for u in users:
        print(dict(u))
except Exception as e:
    print(f"Error: {e}")
conn.close()
