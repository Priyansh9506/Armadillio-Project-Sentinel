"""
Project Sentinel — Trust Engine: Session Context Scoring
Evaluates session metadata for anomalies (time of day in IST, request burst, duration).
"""
from datetime import datetime, timezone, timedelta

# IST offset
IST = timezone(timedelta(hours=5, minutes=30))


def compute_session_score(session_data: dict) -> float:
    """
    Score the session context.
    Returns 0-100.
    """
    score = 100

    # ── Time of Day (IST) ──
    hour = datetime.now(IST).hour
    if not (8 <= hour <= 22):
        score -= 25  # Unusual hours (late night / early morning)

    # ── Request Frequency ──
    requests_per_min = session_data.get("requests_per_minute", 0)
    if requests_per_min > 30:
        score -= 30  # Burst = possible bot or automated tool

    # ── Session Duration ──
    duration_minutes = session_data.get("duration_minutes", 0)
    if duration_minutes > 60:
        score -= 15  # Unusually long session

    # ── IP Reputation (simple check) ──
    ip = session_data.get("ip_address", "")
    if ip.startswith("103.21.") or ip.startswith("10."):
        score -= 10  # Known suspicious range (from our fraud ring data)

    return max(score, 0)
