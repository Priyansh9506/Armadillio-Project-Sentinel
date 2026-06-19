"""
Project Sentinel — Demo Data Seeder
Creates demo users, pre-populates behavioral baselines and sample transactions.
Run this after initializing the database.
"""
import bcrypt
import uuid
from database import get_db, init_db


def seed_demo_data():
    """Seed the database with demo-ready data."""
    init_db()

    with get_db() as db:
        # ── Demo Users ──
        users = [
            ("priyansh", "priyansh@armadillo.dev", "Sentinel2026!", "owner"),
            ("demo_user", "demo@armadillo.dev", "Demo2026!", "demo"),
            ("attacker", "attacker@test.com", "Attack123!", "attacker"),
        ]

        for username, email, password, role in users:
            existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if existing:
                print(f"  [SKIP] User '{username}' already exists, skipping.")
                continue

            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            cursor = db.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            user_id = cursor.lastrowid

            # Create behavioral baseline
            if role == "owner":
                # Pre-populate with realistic typing baseline for the owner
                db.execute("""
                    INSERT INTO behavioral_baselines
                    (user_id, avg_flight_time, avg_dwell_time, avg_typing_speed,
                     avg_mouse_speed, std_flight_time, std_dwell_time, sample_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, 120.5, 78.3, 5.2, 342.5, 28.9, 12.4, 50))
            else:
                db.execute(
                    "INSERT INTO behavioral_baselines (user_id) VALUES (?)",
                    (user_id,)
                )

            print(f"  [OK] Created user: {username} (id={user_id})")

        # ── Demo Transactions (for priyansh) ──
        priyansh = db.execute("SELECT id FROM users WHERE username = 'priyansh'").fetchone()
        if priyansh:
            uid = priyansh["id"]
            existing_txns = db.execute("SELECT COUNT(*) as c FROM transactions WHERE user_id = ?", (uid,)).fetchone()
            if existing_txns["c"] == 0:
                transactions = [
                    (uid, -2000, "Swiggy", "FOOD"),
                    (uid, -15000, "Amazon", "SHOPPING"),
                    (uid, 45000, "Salary Credit", "INCOME"),
                    (uid, -500, "Netflix", "ENTERTAINMENT"),
                    (uid, -1200, "Uber", "TRANSPORT"),
                    (uid, -3500, "Zomato Gold", "FOOD"),
                    (uid, -800, "Spotify", "ENTERTAINMENT"),
                    (uid, -25000, "Rent UPI", "BILLS"),
                    (uid, -1500, "Zerodha", "INVESTMENT"),
                    (uid, -950, "Electricity", "BILLS"),
                ]
                for amount_data in transactions:
                    db.execute(
                        "INSERT INTO transactions (user_id, amount, merchant, category) VALUES (?, ?, ?, ?)",
                        amount_data
                    )
                print(f"  [OK] Seeded {len(transactions)} demo transactions")

        # ── Demo Alerts ──
        alert_count = db.execute("SELECT COUNT(*) as c FROM alerts").fetchone()["c"]
        if alert_count == 0:
            alerts = [
                (priyansh["id"] if priyansh else 1, "NEW_DEVICE", "MEDIUM",
                 "New device detected: Chrome/Win11 from 49.36.x.x"),
                (priyansh["id"] if priyansh else 1, "BEHAVIORAL_ANOMALY", "HIGH",
                 "Typing rhythm deviation detected. Z-score: 2.8"),
            ]
            for alert_data in alerts:
                db.execute(
                    "INSERT INTO alerts (user_id, alert_type, severity, description) VALUES (?, ?, ?, ?)",
                    alert_data
                )
            print(f"  [OK] Seeded {len(alerts)} demo alerts")

    print("\n[DONE] Demo data seeding complete!")
    print("   Login credentials:")
    print("   - priyansh / Sentinel2026!  (legitimate owner)")
    print("   - demo_user / Demo2026!     (second user)")
    print("   - attacker / Attack123!     (for testing)")


if __name__ == "__main__":
    seed_demo_data()
