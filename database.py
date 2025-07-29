import sqlite3
from datetime import datetime

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    count INTEGER DEFAULT 0,
    sub_until TEXT
)
""")
conn.commit()

def get_usage(user_id: int) -> int:
    cursor.execute("SELECT count FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def increment_usage(user_id: int):
    if get_usage(user_id) == 0:
        cursor.execute("INSERT INTO users (user_id, count) VALUES (?, ?)", (user_id, 1))
    else:
        cursor.execute("UPDATE users SET count = count + 1 WHERE user_id=?", (user_id,))
    conn.commit()

def is_subscribed(user_id: int) -> bool:
    cursor.execute("SELECT sub_until FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row and row[0]:
        return datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") > datetime.now()
    return False

def activate_subscription(user_id: int, until: str):
    cursor.execute("UPDATE users SET sub_until=? WHERE user_id=?", (until, user_id))
    conn.commit()
