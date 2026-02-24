import sqlite3
import json
import uuid
from datetime import datetime

import os
# Store DB inside the 'database' folder alongside this script
DB_PATH = os.path.join(os.path.dirname(__file__), "travelsync.db")

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database tables."""
    conn = get_connection()
    c = conn.cursor()
    
    # Schema initialized - Tables will be created if they don't exist


    # Users Table - UPDATED SCHEMA
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        phone_number TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        full_name TEXT,
        password_hash TEXT, -- NULL for Google users
        auth_provider TEXT, -- 'google' or 'manual'
        profile_pic_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Groups Table
    c.execute('''CREATE TABLE IF NOT EXISTS groups (
        group_id TEXT PRIMARY KEY,
        group_name TEXT,
        created_by_phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(created_by_phone) REFERENCES users(phone_number)
    )''')
    
    # Group Members (Junction Table)
    c.execute('''CREATE TABLE IF NOT EXISTS group_members (
        group_id TEXT,
        user_phone TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (group_id, user_phone),
        FOREIGN KEY(group_id) REFERENCES groups(group_id),
        FOREIGN KEY(user_phone) REFERENCES users(phone_number)
    )''')

    # Itinerary Items Table (Linked to Group)
    c.execute('''CREATE TABLE IF NOT EXISTS itinerary_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id TEXT NOT NULL,
        place_name TEXT NOT NULL,
        category TEXT NOT NULL, -- 'place', 'flight', 'train', 'hotel', 'food'
        status TEXT DEFAULT 'Pending', -- 'Pending', 'Visited'
        details TEXT, -- JSON string for extra info
        scheduled_at DATETIME,
        FOREIGN KEY (group_id) REFERENCES groups (group_id)
    )''')
    
    # Chat Logs
    c.execute('''CREATE TABLE IF NOT EXISTS chat_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id TEXT NOT NULL,
        sender TEXT NOT NULL, -- 'User' or 'Agent'
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups (group_id)
    )''')
    
    # Chat Messages (New Table for Group Chat)
    c.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id TEXT,
        sender_phone TEXT,
        sender_name TEXT, -- Cache name to avoid joining tables on every read
        message_content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(group_id) REFERENCES groups(group_id)
    )''')
    
    conn.commit()
    conn.close()

# --- User Management ---

def create_manual_user(phone_number, email, full_name, password_hash):
    """Creates a new user with manual auth."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (phone_number, email, full_name, password_hash, auth_provider)
            VALUES (?, ?, ?, ?, 'manual')
        ''', (phone_number, email, full_name, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def create_google_user(phone_number, email, full_name, profile_pic_url):
    """Creates a new user with Google auth."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (phone_number, email, full_name, auth_provider, profile_pic_url)
            VALUES (?, ?, ?, 'google', ?)
        ''', (phone_number, email, full_name, profile_pic_url))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Error creating Google user: {e}")
        return False
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_phone(phone):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone_number = ?", (phone,))
    user = c.fetchone()
    conn.close()
    return user

def search_users(query):
    """Search by email or phone."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? OR phone_number = ?", (query, query))
    users = c.fetchall()
    conn.close()
    return users

# --- Group Management ---
def create_group(group_name, created_by_phone):
    """Creates a new travel group and returns its ID."""
    group_id = str(uuid.uuid4())
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO groups (group_id, group_name, created_by_phone) VALUES (?, ?, ?)", 
              (group_id, group_name, created_by_phone))
    
    # Add creator as member
    c.execute("INSERT INTO group_members (group_id, user_phone) VALUES (?, ?)", (group_id, created_by_phone))
    
    conn.commit()
    conn.close()
    return group_id

def get_user_groups(phone_number):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT g.* FROM groups g
        JOIN group_members gm ON g.group_id = gm.group_id
        WHERE gm.user_phone = ?
    ''', (phone_number,))
    groups = c.fetchall()
    conn.close()
    return groups

def add_group_member(group_id, user_phone):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO group_members (group_id, user_phone) VALUES (?, ?)", (group_id, user_phone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_group_members(group_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT u.* FROM users u
        JOIN group_members gm ON u.phone_number = gm.user_phone
        WHERE gm.group_id = ?
    ''', (group_id,))
    members = c.fetchall()
    conn.close()
    return members

# --- Itinerary (Updated to use group_id) ---

def get_group(group_id):
    """Fetches group details by ID."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
    group = c.fetchone()
    conn.close()
    return group

def add_itinerary_item(group_id, place_name, category, details=None, scheduled_at=None):
    """Adds a new item to the itinerary."""
    conn = get_connection()
    c = conn.cursor()
    details_json = json.dumps(details) if details else None
    c.execute('''
        INSERT INTO itinerary_items (group_id, place_name, category, details, scheduled_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (group_id, place_name, category, details_json, scheduled_at))
    conn.commit()
    conn.close()

def get_itinerary(group_id):
    """Retrieves all itinerary items for a group."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM itinerary_items WHERE group_id = ?", (group_id,))
    items = c.fetchall()
    conn.close()
    return items

def update_item_status(item_id, status):
    """Updates the status of an itinerary item (e.g., Pending -> Visited)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE itinerary_items SET status = ? WHERE id = ?", (status, item_id))
    conn.commit()
    conn.close()

# --- Chat (V2 - Using chat_messages table) ---

def update_group_insider_data(group_id, insider_json):
    """Updates the insider_data for a group."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE groups SET insider_data = ? WHERE group_id = ?", (insider_json, group_id))
    conn.commit()
    conn.close()

def get_group_insider_data(group_id):
    """Fetches insider_data for a group."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT insider_data FROM groups WHERE group_id = ?", (group_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def send_chat_message(group_id, sender_phone, sender_name, message, reply_to_id=None):
    """Sends a message to the group chat."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO chat_messages (group_id, sender_phone, sender_name, message_content, reply_to_id)
                 VALUES (?, ?, ?, ?, ?)''', (group_id, sender_phone, sender_name, message, reply_to_id))
    conn.commit()
    conn.close()

def fetch_chat_messages(group_id):
    """Retrieves chat messages for a group, including reply context."""
    conn = get_connection()
    c = conn.cursor()
    # Self-join to get the replied message's content
    c.execute('''
        SELECT 
            m.message_id, m.group_id, m.sender_phone, m.sender_name, m.message_content, m.timestamp, m.reply_to_id,
            r.sender_name as reply_sender,
            r.message_content as reply_content
        FROM chat_messages m
        LEFT JOIN chat_messages r ON m.reply_to_id = r.message_id
        WHERE m.group_id = ? 
        ORDER BY m.timestamp ASC
    ''', (group_id,))
    msgs = c.fetchall()
    conn.close()
    return msgs

if __name__ == "__main__":
    init_db()
    print("Database re-initialized")
