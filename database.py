import sqlite3
from datetime import datetime, timezone
from flask import g, current_app


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS perfumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unique_code TEXT NOT NULL UNIQUE,
            perfume_name TEXT NOT NULL,
            brand_name TEXT NOT NULL,
            batch_number TEXT NOT NULL,
            box_serial_number TEXT NOT NULL UNIQUE,
            manufacturing_date TEXT NOT NULL,
            authorized_seller TEXT NOT NULL,
            place_of_sale TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Genuine',
            scan_count INTEGER NOT NULL DEFAULT 0,
            scan_threshold INTEGER NOT NULL DEFAULT 5,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            perfume_id INTEGER,
            unique_code TEXT NOT NULL,
            scanned_at TEXT NOT NULL,
            result_status TEXT NOT NULL,
            user_agent TEXT,
            notes TEXT,
            FOREIGN KEY (perfume_id) REFERENCES perfumes(id)
        );

        CREATE TABLE IF NOT EXISTS invalid_scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempted_code TEXT NOT NULL,
            scanned_at TEXT NOT NULL,
            result_status TEXT NOT NULL,
            user_agent TEXT
        );
        """
    )
    db.commit()


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def fetch_one(query, args=()):
    return get_db().execute(query, args).fetchone()


def fetch_all(query, args=()):
    return get_db().execute(query, args).fetchall()
