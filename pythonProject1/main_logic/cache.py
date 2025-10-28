import json
import sqlite3
import os
from datetime import datetime, timedelta

# Default path for the SQLite cache database
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "cache.db"))


def init_db(db_path: str = None):
    """
    Initialize the cache database and table.
    Args: db_path (str, optional): Custom database file path.
    """
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
    """
    Retrieve a cached menu entry if it exists and is not expired.

    Args:
    url (str): The restaurant webpage URL.
    date (str): The date string for which to retrieve the cache.
    max_age_hours (int, optional): Maximum allowed cache age in hours. Defaults to 6.
    db_path (str, optional): Custom path to the cache database.

    Returns:
    dict | None: Cached menu data as a dictionary if found and not expired,
    otherwise None.
    """
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
    """
    Save or update a restaurant menu in the cache.

    If a record already exists for the same URL and date, it is replaced.
    The creation timestamp is stored in UTC to support cleanup and expiration.

    Args:
    url (str): The restaurant webpage URL.
    date (str): The date string for the cached menu.
    data (dict): The menu data to cache.
    db_path (str, optional): Custom path to the cache database.
    """
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO cache (url, date, data, created_at)
        VALUES (?, ?, ?, ?)
    """, (url, date, json.dumps(data), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def cleanup_old_cache(hours: int = 12, db_path: str = None):
    """
    Delete old cache entries older than the specified number of hours.

    This function helps keep the cache small and relevant by periodically
    removing outdated entries.

    Args:
    hours (int, optional): Maximum time (in hours) before cache entries are deleted. Defaults to 12.
    db_path (str, optional): Custom path to the cache database.
    """
    path = db_path or DB_PATH
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DELETE FROM cache WHERE created_at < ?", (cutoff,))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    print(f"Cache cleanup: removed {deleted} old entries (older than {hours} hours).")


init_db()
cleanup_old_cache()

