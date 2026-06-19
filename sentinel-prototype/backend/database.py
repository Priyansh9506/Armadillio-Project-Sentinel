"""
Project Sentinel — SQLite Database Setup
Creates all tables and provides a connection helper.
"""
import sqlite3
from contextlib import contextmanager
from config import DB_PATH


def init_db():
    """Create all tables if they don't exist."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            totp_secret TEXT,
            upi_pin_hash TEXT,
            duress_pin TEXT DEFAULT '9999',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS behavioral_baselines (
            user_id INTEGER PRIMARY KEY,
            avg_flight_time REAL DEFAULT 0,
            avg_dwell_time REAL DEFAULT 0,
            avg_typing_speed REAL DEFAULT 0,
            avg_mouse_speed REAL DEFAULT 0,
            std_flight_time REAL DEFAULT 0,
            std_dwell_time REAL DEFAULT 0,
            sample_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS trust_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id TEXT,
            trust_score REAL,
            behavioral_score REAL,
            device_score REAL,
            session_score REAL,
            graph_score REAL,
            transaction_score REAL,
            geo_score REAL,
            decision TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            alert_type TEXT,
            severity TEXT,
            description TEXT,
            resolved INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            device_fingerprint TEXT,
            ip_address TEXT,
            geo_city TEXT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            merchant TEXT,
            category TEXT,
            is_duress INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS push_auth_challenges (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            user_id INTEGER,
            correct_number INTEGER,
            status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    conn.commit()
    conn.close()
    print("[OK] Database initialized at:", DB_PATH)


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
