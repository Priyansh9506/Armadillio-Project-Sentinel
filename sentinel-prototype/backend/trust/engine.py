"""
Project Sentinel — Trust Engine: Composite Scoring & Decision Gateway
Combines all sub-scores into a single trust score and makes the ALLOW/STEP_UP/BLOCK decision.
"""
from datetime import datetime
from database import get_db
from trust.behavioral import compute_behavioral_score, update_baseline
from trust.device import compute_device_score
from trust.session import compute_session_score

from config import TRUST_ALLOW_THRESHOLD, TRUST_STEP_UP_THRESHOLD
import numpy as np


def compute_transaction_score(user_id: int, current_amount: float) -> float:
    """
    Checks if a transfer amount is anomalous vs. the user's history.
    Returns 0-100.
    """
    with get_db() as db:
        rows = db.execute(
            "SELECT amount FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50",
            (user_id,)
        ).fetchall()

    amounts = [r["amount"] for r in rows]
    if len(amounts) < 5:
        return 100  # Not enough history

    avg_spend = float(np.mean(amounts))
    std_spend = float(np.std(amounts))

    z_score = abs(current_amount - avg_spend) / max(std_spend, 1)

    if z_score > 3.0:
        return 15   # Extreme anomaly
    elif z_score > 2.0:
        return 50   # Warning
    return 100      # Normal


def check_impossible_travel(current_city: str, last_city: str, time_diff_hours: float) -> float:
    """
    Simplified geo-velocity check.
    If user changes cities in impossibly short time, return 0.
    """
    # Simple city-pair distance lookup (km) for demo
    CITY_DISTANCES = {
        frozenset({"Mumbai", "Delhi"}): 1400,
        frozenset({"Mumbai", "Bangalore"}): 980,
        frozenset({"Delhi", "Kolkata"}): 1500,
        frozenset({"Chennai", "Delhi"}): 2180,
        frozenset({"Ahmedabad", "Delhi"}): 940,
        frozenset({"Ahmedabad", "Mumbai"}): 530,
    }

    if not current_city or not last_city or current_city == last_city:
        return 100  # Same city or unknown — no anomaly

    pair = frozenset({current_city, last_city})
    distance = CITY_DISTANCES.get(pair, 500)  # Default 500km for unknown pairs

    if time_diff_hours <= 0.01:
        time_diff_hours = 0.01

    velocity = distance / time_diff_hours  # km/h

    if velocity > 1000:  # Faster than a commercial jet
        return 0  # Impossible travel!
    elif velocity > 500:
        return 30  # Suspicious
    return 100


def compute_trust_score(
    user_id: int,
    session_id: str,
    telemetry: dict,
    session_data: dict,
    device_fingerprint: dict = None,
    transaction_amount: float = None,
    current_city: str = None,
    last_city: str = None,
    time_since_last_hours: float = 24.0,
) -> dict:
    """
    The main Trust Engine — computes composite score from all dimensions.
    Returns a dict with scores, decision, and context.
    """
    # ── Fetch baseline ──
    with get_db() as db:
        baseline = db.execute(
            "SELECT * FROM behavioral_baselines WHERE user_id = ?", (user_id,)
        ).fetchone()
        baseline = dict(baseline) if baseline else {}

        known_fps = db.execute(
            "SELECT device_fingerprint FROM sessions WHERE user_id = ? GROUP BY device_fingerprint",
            (user_id,)
        ).fetchall()
        known_fps = [r["device_fingerprint"] for r in known_fps if r["device_fingerprint"]]

    # ── Compute sub-scores ──
    behavioral = compute_behavioral_score(telemetry, baseline)
    device = compute_device_score(device_fingerprint or {}, known_fps)
    session = compute_session_score(session_data)
    transaction = compute_transaction_score(user_id, transaction_amount) if transaction_amount else 100
    geo = check_impossible_travel(current_city, last_city, time_since_last_hours)

    # ── Graph score (placeholder — will be Neo4j query) ──
    graph = 100

    # ── Impossible travel = instant block ──
    if geo == 0:
        composite = 0
        decision = "BLOCK"
    else:
        composite = (
            0.30 * behavioral +
            0.20 * device +
            0.15 * session +
            0.20 * graph +
            0.15 * transaction
        )

        if composite > TRUST_ALLOW_THRESHOLD:
            decision = "ALLOW"
        elif composite > TRUST_STEP_UP_THRESHOLD:
            decision = "STEP_UP"
        else:
            decision = "BLOCK"

    # ── Determine MFA method if STEP_UP ──
    mfa_method = None
    if decision == "STEP_UP":
        mfa_method = _select_mfa_method(behavioral, device, geo)

    # ── Update baseline (only if it looks like the real user) ──
    if behavioral > 70 and baseline.get("sample_count", 0) < 200:
        with get_db() as db:
            update_baseline(user_id, telemetry, db)

    # ── Log the trust event ──
    with get_db() as db:
        db.execute("""
            INSERT INTO trust_logs
            (user_id, session_id, trust_score, behavioral_score, device_score,
             session_score, graph_score, transaction_score, geo_score, decision)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, session_id, composite, behavioral, device,
              session, graph, transaction, geo, decision))

        # Generate alert if blocked
        if decision == "BLOCK":
            db.execute("""
                INSERT INTO alerts (user_id, alert_type, severity, description)
                VALUES (?, ?, ?, ?)
            """, (user_id, "ATO_SUSPECTED", "CRITICAL",
                  f"Trust score dropped to {composite:.0f}. Decision: {decision}"))

    return {
        "trust_score": round(composite, 1),
        "decision": decision,
        "mfa_method": mfa_method,
        "sub_scores": {
            "behavioral": round(behavioral, 1),
            "device": round(device, 1),
            "session": round(session, 1),
            "graph": round(graph, 1),
            "transaction": round(transaction, 1),
            "geo_velocity": round(geo, 1),
        }
    }


def _select_mfa_method(behavioral: float, device: float, geo: float) -> str:
    """Adaptive MFA selection based on WHY trust dropped."""
    if behavioral < 50:
        return "VOICE_LIVENESS"  # Different person typing — biometric needed
    if device < 50:
        return "PUSH_AUTH"       # New device — push auth to trusted device
    if geo < 50:
        return "PUSH_AUTH"       # Unusual location
    return "PUSH_AUTH"           # Default
