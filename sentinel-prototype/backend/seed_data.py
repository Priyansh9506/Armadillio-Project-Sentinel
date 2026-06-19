import sqlite3
import bcrypt
import hashlib
from datetime import datetime, timedelta
import random
from config import DB_PATH

def seed():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    print(f"Seeding database at {DB_PATH}")

    # Clear existing data for fresh seed (optional, but good for hackathons)
    # Be careful not to delete the user 'priyansh' if they already registered.
    
    # Let's just insert alerts and past trust logs for the SOC dashboard
    
    # Common Password and PIN Hashes
    pwd_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode('utf-8')
    upi_pin_hash = hashlib.sha256(b"1234").hexdigest()

    mock_users = [
        ("priyansh", "priyansh@armadillo.com", "Priyansh Patel", "100010001000", "priyansh@bob", "9876543210"),
        ("vyom", "vyom@armadillo.com", "Vyom Patel", "200020002000", "vyom@bob", "9123456789"),
        ("chirag", "chirag@armadillo.com", "Chirag Bhanushali", "300030003000", "chirag@bob", "9988776655")
    ]

    user_ids = []
    for uname, email, fullname, acc_no, upi, phone in mock_users:
        try:
            cursor.execute(
                """INSERT INTO users (username, email, password_hash, upi_pin_hash, account_no, upi_id, phone_no) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (uname, email, pwd_hash, upi_pin_hash, acc_no, upi, phone)
            )
            user_ids.append(cursor.lastrowid)
        except sqlite3.IntegrityError:
            cursor.execute("SELECT id FROM users WHERE username = ?", (uname,))
            user_ids.append(cursor.fetchone()[0])

    priyansh_id, victim_id, insider_id = user_ids

    # Seed Alerts
    alerts = [
        (victim_id, "ATO_SUSPECTED", "HIGH", "Account Takeover Suspected: Drastic change in typing speed and mouse flight patterns detected for victim_demo."),
        (insider_id, "INSIDER_THREAT", "CRITICAL", "Insider Threat: Bulk PII access by employee 'insider_threat' outside normal hours."),
        (victim_id, "FRAUD_RING", "CRITICAL", "Fraud Ring Detected: Device fingerprint matches known mule account network (MULE-9981)."),
        (victim_id, "DURESS_TRANSFER", "CRITICAL", "Duress Alert: Silent alarm triggered during transfer of ₹50,000 to XXXX-4521.")
    ]
    
    now = datetime.utcnow()
    for user_id, a_type, sev, desc in alerts:
        t = now - timedelta(hours=random.randint(1, 48), minutes=random.randint(1, 60))
        cursor.execute(
            "INSERT INTO alerts (user_id, alert_type, severity, description, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_id, a_type, sev, desc, t.strftime("%Y-%m-%d %H:%M:%S"))
        )

    # Seed active session for insider
    session_id = "mock_sess_" + str(random.randint(1000,9999))
    cursor.execute(
        "INSERT INTO sessions (session_id, user_id, device_fingerprint, ip_address, geo_city, is_active) VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, insider_id, "mock_fingerprint_xyz", "103.21.34.12", "Mumbai", 1)
    )

    # Seed Trust Logs for insider to make the SOC look busy
    for i in range(10):
        t = now - timedelta(minutes=i*3)
        score = random.uniform(30.0, 50.0)
        cursor.execute(
            "INSERT INTO trust_logs (user_id, session_id, trust_score, behavioral_score, decision, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (insider_id, session_id, score, score, "BLOCK", t.strftime("%Y-%m-%d %H:%M:%S"))
        )

    # Add a mock duress transaction
    cursor.execute(
        "INSERT INTO transactions (user_id, amount, merchant, category, is_duress) VALUES (?, ?, ?, ?, ?)",
        (victim_id, 50000.0, "HELD_FOR_XXXX-4521", "DURESS_HOLD", 1)
    )

    # ---- SEED CLEAN DATA FOR PRIYANSH ----
    try:
        cursor.execute("SELECT id FROM users WHERE username = 'priyansh'")
        row = cursor.fetchone()
        if row:
            priyansh_id = row[0]
            
            # Insert a healthy behavioral baseline for ALL mocked users so ML Model works
            for uid in user_ids:
                cursor.execute("""
                    INSERT OR REPLACE INTO behavioral_baselines 
                    (user_id, avg_flight_time, avg_dwell_time, avg_typing_speed, avg_mouse_speed, sample_count) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (uid, 150.0, 80.0, 5.0, 300.0, 100))

            # Insert normal transactions
            transactions = [
                (25000.0, "Salary Credit", "Income"),
                (-450.0, "Swiggy", "Food"),
                (-1200.0, "Amazon", "Shopping"),
                (-150.0, "Uber", "Transport"),
                (-3000.0, "Electricity Bill", "Utilities")
            ]
            for amt, mcht, cat in transactions:
                t = now - timedelta(days=random.randint(1, 15))
                cursor.execute(
                    "INSERT INTO transactions (user_id, amount, merchant, category, is_duress, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                    (priyansh_id, amt, mcht, cat, 0, t.strftime("%Y-%m-%d %H:%M:%S"))
                )

            # Insert healthy trust logs
            for i in range(15):
                t = now - timedelta(minutes=i*15)
                score = random.uniform(88.0, 98.0)
                cursor.execute(
                    "INSERT INTO trust_logs (user_id, session_id, trust_score, behavioral_score, decision, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                    (priyansh_id, "clean_session_123", score, score, "ALLOW", t.strftime("%Y-%m-%d %H:%M:%S"))
                )
    except Exception as e:
        print("Could not seed data for priyansh (user might not exist yet).", e)

    conn.commit()
    conn.close()
    print("Seed complete. SOC dashboard should now show alerts and stats.")

if __name__ == "__main__":
    seed()
