"""
Project Sentinel — Postgres Database Setup
Connects to Supabase Postgres.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv

from config import BASE_DIR

load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")

class PostgresDBWrapper:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, sql, parameters=None):
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        if parameters:
            cursor.execute(sql, parameters)
        else:
            cursor.execute(sql)
        return cursor
        
    def commit(self):
        self.conn.commit()
        
    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

def init_db():
    """Create all tables if they don't exist."""
    if not DATABASE_URL:
        print("[WARN] DATABASE_URL not set!")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            totp_secret TEXT,
            upi_pin_hash TEXT,
            duress_pin TEXT DEFAULT '9999',
            account_no TEXT,
            upi_id TEXT,
            phone_no TEXT,
            balance REAL DEFAULT 100000.0,
            has_pin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS account_balances (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
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
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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


        CREATE TABLE IF NOT EXISTS push_auth_challenges (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            user_id INTEGER,
            correct_number INTEGER,
            status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        CREATE TABLE IF NOT EXISTS bank_accounts (
            upi_id TEXT PRIMARY KEY,
            account_no TEXT UNIQUE,
            name_of_customer TEXT,
            balance REAL DEFAULT 0.0
        );
    """)

    conn.commit()
    conn.close()
    print("[OK] Database initialized at Supabase PostgreSQL")


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = psycopg2.connect(DATABASE_URL)
    db_wrapper = PostgresDBWrapper(conn)
    try:
        yield db_wrapper
        db_wrapper.commit()
    except Exception:
        db_wrapper.rollback()
        raise
    finally:
        db_wrapper.close()

if __name__ == "__main__":
    init_db()
