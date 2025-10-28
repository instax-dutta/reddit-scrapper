"""
SQLite database schema and helpers for Reddit Scraper
"""

import os
import sqlite3
from typing import Iterable, Dict, Any

DB_PATH = os.path.join("data", "app.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def init_schema() -> None:
    conn = get_connection()
    cur = conn.cursor()
    # sessions table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            session_date TEXT NOT NULL,
            total_leads INTEGER DEFAULT 0,
            high_priority_leads INTEGER DEFAULT 0,
            leads_with_contact INTEGER DEFAULT 0,
            replies_posted INTEGER DEFAULT 0,
            ai_analysis_enabled INTEGER DEFAULT 0
        );
        """
    )
    # leads table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            title TEXT,
            content TEXT,
            author TEXT,
            subreddit TEXT,
            url TEXT,
            score INTEGER,
            comments INTEGER,
            service_category TEXT,
            client_score INTEGER,
            decision_maker INTEGER,
            contact_readiness TEXT,
            urgency_level TEXT,
            engagement_score REAL,
            engagement_level TEXT,
            lead_quality_score REAL,
            lead_priority TEXT,
            created_utc TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );
        """
    )
    # replies table (optional)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            post_id TEXT,
            subreddit TEXT,
            author TEXT,
            reply_text TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );
        """
    )
    conn.commit()
    conn.close()


def upsert_many(table: str, rows: Iterable[Dict[str, Any]]) -> None:
    rows = list(rows)
    if not rows:
        return
    conn = get_connection()
    cols = list(rows[0].keys())
    placeholders = ",".join([":" + c for c in cols])
    col_sql = ",".join(cols)
    sql = f"INSERT OR REPLACE INTO {table} ({col_sql}) VALUES ({placeholders});"
    conn.executemany(sql, rows)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_schema()
    print(f"✓ Database initialized at {DB_PATH}")


