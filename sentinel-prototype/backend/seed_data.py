import psycopg2
import bcrypt
import hashlib
from datetime import datetime, timedelta
import random
import os
from database import get_db

def seed():
    print("Seeding database at Supabase Postgres...")

    import os
    pwd_pepper = os.getenv("PASSWORD_PEPPER", "default_secret_password_pepper").encode()
    peppered_pwd = b"password123" + pwd_pepper
    pwd_hash = bcrypt.hashpw(peppered_pwd, bcrypt.gensalt()).decode('utf-8')
    
    pepper = os.getenv("PIN_PEPPER", "default_secret_pepper").encode()
    peppered_pin = b"1234" + pepper
    upi_pin_hash = bcrypt.hashpw(peppered_pin, bcrypt.gensalt()).decode('utf-8')

    mock_users = [
        ("priyansh", "priyansh@armadillo.com", "Priyansh Patel", "100010001000", "priyansh@bob", "9876543210", 452380.0),
        ("vyom", "vyom@armadillo.com", "Vyom Patel", "200020002000", "vyom@bob", "9123456789", 452380.0),
        ("chirag", "chirag@armadillo.com", "Chirag Bhanushali", "300030003000", "chirag@bob", "9988776655", 150000.0)
    ]

    with get_db() as db:
        user_ids = []
        for uname, email, fullname, acc_no, upi, phone, balance in mock_users:
            try:
                cursor = db.execute(
                    """INSERT INTO users (username, email, password_hash, upi_pin_hash, account_no, upi_id, phone_no, balance, has_pin) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE) RETURNING id""",
                    (uname, email, pwd_hash, upi_pin_hash, acc_no, upi, phone, balance)
                )
                user_id = cursor.fetchone()['id']
                user_ids.append(user_id)
                db.execute("INSERT INTO account_balances (user_id, balance) VALUES (%s, %s)", (user_id, balance))
            except psycopg2.IntegrityError:
                db.rollback()
                cursor = db.execute("SELECT id FROM users WHERE username = %s", (uname,))
                user_id = cursor.fetchone()['id']
                user_ids.append(user_id)
                try:
                    db.execute("INSERT INTO account_balances (user_id, balance) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING", (user_id, balance))
                except Exception:
                    db.rollback()

            # Push to Supabase Cloud if needed (but we are already in Supabase now!)
            # So we just insert into bank_accounts table directly
            try:
                db.execute("""
                    INSERT INTO bank_accounts (upi_id, account_no, name_of_customer, balance)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (upi_id) DO UPDATE SET balance = EXCLUDED.balance
                """, (upi, acc_no, fullname, balance))
            except Exception as e:
                db.rollback()

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
            db.execute(
                "INSERT INTO alerts (user_id, alert_type, severity, description, timestamp) VALUES (%s, %s, %s, %s, %s)",
                (user_id, a_type, sev, desc, t.strftime("%Y-%m-%d %H:%M:%S"))
            )

        # Seed active session for insider
        session_id = "mock_sess_" + str(random.randint(1000,9999))
        try:
            db.execute(
                "INSERT INTO sessions (session_id, user_id, device_fingerprint, ip_address, geo_city, is_active) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (session_id) DO NOTHING",
                (session_id, insider_id, "mock_fingerprint_xyz", "103.21.34.12", "Mumbai", 1)
            )
        except Exception:
            db.rollback()

        # Seed Trust Logs for insider
        for i in range(10):
            t = now - timedelta(minutes=i*3)
            score = random.uniform(30.0, 50.0)
            db.execute(
                "INSERT INTO trust_logs (user_id, session_id, trust_score, behavioral_score, decision, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
                (insider_id, session_id, score, score, "BLOCK", t.strftime("%Y-%m-%d %H:%M:%S"))
            )

        # Add a mock duress transaction
        db.execute(
            "INSERT INTO transactions (user_id, amount, merchant, category, is_duress) VALUES (%s, %s, %s, %s, %s)",
            (victim_id, 50000.0, "HELD_FOR_XXXX-4521", "DURESS_HOLD", 1)
        )

        # Seed clean data for priyansh
        cursor = db.execute("SELECT id FROM users WHERE username = 'priyansh'")
        row = cursor.fetchone()
        if row:
            priyansh_id = row['id']
            for uid in user_ids:
                try:
                    db.execute("""
                        INSERT INTO behavioral_baselines 
                        (user_id, avg_flight_time, avg_dwell_time, avg_typing_speed, avg_mouse_speed, sample_count) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id) DO UPDATE SET 
                        avg_flight_time = EXCLUDED.avg_flight_time
                    """, (uid, 150.0, 80.0, 5.0, 300.0, 100))
                except Exception:
                    db.rollback()

            transactions = [
                (25000.0, "Salary Credit", "Income"),
                (-450.0, "Swiggy", "Food"),
                (-1200.0, "Amazon", "Shopping"),
                (-150.0, "Uber", "Transport"),
                (-3000.0, "Electricity Bill", "Utilities")
            ]
            for amt, mcht, cat in transactions:
                t = now - timedelta(days=random.randint(1, 15))
                db.execute(
                    "INSERT INTO transactions (user_id, amount, merchant, category, is_duress, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
                    (priyansh_id, amt, mcht, cat, 0, t.strftime("%Y-%m-%d %H:%M:%S"))
                )

            for i in range(15):
                t = now - timedelta(minutes=i*15)
                score = random.uniform(88.0, 98.0)
                db.execute(
                    "INSERT INTO trust_logs (user_id, session_id, trust_score, behavioral_score, decision, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
                    (priyansh_id, "clean_session_123", score, score, "ALLOW", t.strftime("%Y-%m-%d %H:%M:%S"))
                )

        print("Seed complete. Data inserted to Supabase.")

if __name__ == "__main__":
    seed()
