import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "travelsync.db")

def test_emoji():
    print(f"Testing DB at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Create table if not exists (handling my local test env)
    # (Assuming table exists from previous steps, but let's be safe for this isolated test)
    
    # 2. Insert Emoji
    TEST_MSG = "Hello 🌍! ✈️🚀"
    TEST_GROUP = "test_group_emoji"
    
    print(f"Inserting: {TEST_MSG}")
    try:
        # We need a dummy group to satisfy foreign key? 
        # Actually my schema has FKs. I should use an existing group or disable FK for test.
        c.execute("PRAGMA foreign_keys = OFF;") 
        
        c.execute("INSERT INTO chat_messages (group_id, sender_phone, sender_name, message_content) VALUES (?, ?, ?, ?)", 
                  (TEST_GROUP, "0000000000", "EmojiTester", TEST_MSG))
        conn.commit()
        
        # 3. Read it back
        c.execute("SELECT message_content FROM chat_messages WHERE group_id = ? AND sender_name = ?", (TEST_GROUP, "EmojiTester"))
        row = c.fetchone()
        
        if row:
            content = row[0]
            print(f"Retrieved: {content}")
            if content == TEST_MSG:
                print("SUCCESS: Emojis match perfectly!")
            else:
                print(f"FAILURE: Content mismatch. Got '{content}'")
        else:
            print("FAILURE: Could not find message.")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        # Cleanup
        c.execute("DELETE FROM chat_messages WHERE group_id = ?", (TEST_GROUP,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    test_emoji()
