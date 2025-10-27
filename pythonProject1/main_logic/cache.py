import json
import sqlite3
import os
from datetime import datetime, timedelta


DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "cache.db"))


def init_db(db_path: str = None):
    """Initialize the cache database and table."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS cache (
        url TEXT,
        date TEXT,
        data TEXT,
        created_at TEXT,
        PRIMARY KEY (url, date)
    )
    """)
    conn.commit()
    conn.close()


def get_cached_menu(url: str, date: str, max_age_hours: int = 6, db_path: str = None):
    """Return cached menu if it exists and is not expired."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT data, created_at FROM cache WHERE url=? AND date=?", (url, date))
    row = c.fetchone()
    conn.close()

    if not row:
        return None

    data_str, created_at_str = row
    created_at = datetime.fromisoformat(created_at_str)
    if datetime.utcnow() - created_at > timedelta(hours=max_age_hours):
        return None

    return json.loads(data_str)


def save_menu_to_cache(url: str, date: str, data: dict, db_path: str = None):
    """Save menu to cache, replacing any existing entry for the same URL and date."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO cache (url, date, data, created_at)
        VALUES (?, ?, ?, ?)
    """, (url, date, json.dumps(data), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def cleanup_old_cache(days: int = 7, db_path: str = None):
    """Delete cache entries older than given days."""
    path = db_path or DB_PATH
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DELETE FROM cache WHERE created_at < ?", (cutoff,))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    print(f"Cache cleanup: removed {deleted} old entries.")


init_db()
cleanup_old_cache()

