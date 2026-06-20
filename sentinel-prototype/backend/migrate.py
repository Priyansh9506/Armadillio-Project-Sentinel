import sqlite3
import bcrypt
import os

def run_migration():
    db_path = os.path.join(os.path.dirname(__file__), "sentinel.db")
    print(f"Connecting to {db_path}")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE users ADD COLUMN upi_pin_hash TEXT")
        print("Column upi_pin_hash added.")
        
        # Set a default pin (1234) for existing users
        default_hash = bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode()
        c.execute("UPDATE users SET upi_pin_hash = %s", (default_hash,))
        conn.commit()
        print("Default PIN 1234 set for all existing users.")
    except sqlite3.OperationalError as e:
        print("Migration error (maybe column already exists?):", e)
    conn.close()

if __name__ == "__main__":
    run_migration()
