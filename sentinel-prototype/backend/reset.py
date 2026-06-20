import sys
import bcrypt
import sqlite3
from pathlib import Path

DB_PATH = Path("sentinel.db")

def reset_password():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password = "Sentinel2026!"
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    cursor.execute("UPDATE users SET password_hash = %s WHERE username = 'priyansh'", (password_hash,))
    conn.commit()
    print("Password reset for priyansh to Sentinel2026!")

if __name__ == "__main__":
    reset_password()
