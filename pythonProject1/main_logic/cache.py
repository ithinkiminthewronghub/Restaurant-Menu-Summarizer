import json
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "cache.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS cache (
        url TEXT,
        date TEXT,
        data TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()


def get_cached_menu(url, date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT data FROM cache WHERE url=? AND date=?", (url, date))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None


def save_menu_to_cache(url, date, data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO cache (url, date, data, created_at) VALUES (?, ?, ?, ?)",
              (url, date, json.dumps(data), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def cleanup_old_cache(days: int = 1):
    """Deletes cache entries older than 1 day"""
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM cache WHERE created_at < ?", (cutoff,))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    print(f"Cache cleanup: removed {deleted} old entries.")


init_db()
cleanup_old_cache()
