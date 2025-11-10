# db.py
import sqlite3
from datetime import datetime

DB = "data.db"

def get_conn():
    conn = sqlite3.connect(DB, check_same_thread=False)
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # owners table (one row per owner)
    c.execute("""
    CREATE TABLE IF NOT EXISTS owners (
        owner_id INTEGER PRIMARY KEY,
        username TEXT,
        registered_at TEXT,
        description TEXT,
        category TEXT,
        logo_file_id TEXT,
        premium_status TEXT DEFAULT 'free',
        verified INTEGER DEFAULT 0
    )
    """)
    # channels: multiple channels per owner
    c.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        channel_name TEXT,
        start_link TEXT,
        created_at TEXT
    )
    """)
    # users (people who message via owner link)
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        alias TEXT,
        started_at TEXT
    )
    """)
    # mapping forwarded messages to user for reply correlation
    c.execute("""
    CREATE TABLE IF NOT EXISTS forwarded_map (
        forwarded_msg_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        owner_id INTEGER,
        created_at TEXT
    )
    """)
    # analytics (basic)
    c.execute("""
    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        event TEXT,
        metadata TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

# Owner functions
def register_owner(owner_id, username, description=None, category=None, logo_file_id=None):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    # if owner exists, update username; else insert
    c.execute("INSERT OR REPLACE INTO owners (owner_id, username, registered_at, description, category, logo_file_id) VALUES (?, ?, COALESCE((SELECT registered_at FROM owners WHERE owner_id=?), ?), ?, ?, ?)",
              (owner_id, username, owner_id, now, description, category, logo_file_id))
    conn.commit()
    conn.close()

def set_owner_field(owner_id, field, value):
    if field not in ("description","category","logo_file_id","premium_status","verified","username"):
        return
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"UPDATE owners SET {field} = ? WHERE owner_id = ?", (value, owner_id))
    conn.commit()
    conn.close()

def is_owner_registered(owner_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT 1 FROM owners WHERE owner_id = ?", (owner_id,))
    found = c.fetchone() is not None
    conn.close()
    return found

def get_owner(owner_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT owner_id, username, description, category, logo_file_id, premium_status, verified FROM owners WHERE owner_id = ?", (owner_id,))
    row = c.fetchone()
    conn.close()
    return row

# Channels
def add_channel(owner_id, channel_name, start_link=None):
    conn = get_conn()
    c = conn.cursor()
    created = datetime.utcnow().isoformat()
    c.execute("INSERT INTO channels (owner_id, channel_name, start_link, created_at) VALUES (?, ?, ?, ?)",
              (owner_id, channel_name, start_link, created))
    conn.commit()
    conn.close()

def get_channels_of_owner(owner_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT channel_id, channel_name, start_link, created_at FROM channels WHERE owner_id = ?", (owner_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# Users
def ensure_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    alias = f"User#{str(user_id)[-4:]}"
    c.execute("INSERT OR IGNORE INTO users (user_id, alias, started_at) VALUES (?, ?, ?)",
              (user_id, alias, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def set_alias(user_id, alias):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET alias = ? WHERE user_id = ?", (alias, user_id))
    conn.commit()
    conn.close()

def get_user_alias(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT alias FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# Forwarded mapping
def save_forwarded_map(forwarded_msg_id, user_id, owner_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO forwarded_map (forwarded_msg_id, user_id, owner_id, created_at) VALUES (?, ?, ?, ?)",
              (forwarded_msg_id, user_id, owner_id, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_user_by_forwarded_msg(forwarded_msg_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id, owner_id FROM forwarded_map WHERE forwarded_msg_id = ?", (forwarded_msg_id,))
    row = c.fetchone()
    conn.close()
    return (row[0], row[1]) if row else (None, None)

# Analytics simple
def add_analytic(owner_id, event, metadata=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO analytics (owner_id, event, metadata, created_at) VALUES (?, ?, ?, ?)",
              (owner_id, event, metadata, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def owner_stats(owner_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM forwarded_map WHERE owner_id = ?", (owner_id,))
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT user_id) FROM forwarded_map WHERE owner_id = ?", (owner_id,))
    users = c.fetchone()[0]
    conn.close()
    return {"messages_forwarded": total, "unique_users": users}
