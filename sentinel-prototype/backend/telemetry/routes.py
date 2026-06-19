"""
Project Sentinel — Telemetry Routes
Receives keystroke/mouse/device telemetry from the frontend SDK.
Uses proper auth dependency and real session data.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta

from auth.routes import get_current_user
from database import get_db
from trust.engine import compute_trust_score

router = APIRouter()


class TelemetryPayload(BaseModel):
    session_id: str
    keystroke_metrics: Optional[dict] = None
    mouse_metrics: Optional[dict] = None
    device_fingerprint: Optional[dict] = None
    transaction_amount: Optional[float] = None
    current_city: Optional[str] = None


@router.post("/ingest")
async def ingest_telemetry(payload: TelemetryPayload, user: dict = Depends(get_current_user)):
    """
    Main telemetry ingestion endpoint.
    Receives behavioral data every 3 seconds and returns updated trust score.
    Authenticated via shared get_current_user dependency.
    """
    user_id = user["user_id"]
    session_id = payload.session_id

    # Validate session belongs to this user and is active
    with get_db() as db:
        session = db.execute(
            "SELECT * FROM sessions WHERE session_id = ? AND user_id = ?",
            (session_id, user_id)
        ).fetchone()

        if not session:
            return {"error": "Session not found", "trust_score": 0, "decision": "BLOCK"}

        if session["is_active"] == 0:
            return {"error": "Session is inactive", "trust_score": 0, "decision": "BLOCK"}

        # Compute real session duration
        start_time_str = session["start_time"]
        try:
            start_dt = datetime.strptime(str(start_time_str).split('.')[0], "%Y-%m-%d %H:%M:%S")
            start_dt = start_dt.replace(tzinfo=timezone.utc)
            duration_minutes = (datetime.now(timezone.utc) - start_dt).total_seconds() / 60.0
        except Exception:
            duration_minutes = 5.0

        # Update last_activity timestamp
        db.execute(
            "UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_id = ?",
            (session_id,)
        )

        # Count telemetry events in last minute for request rate
        one_minute_ago = (datetime.now(timezone.utc) - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
        rate_row = db.execute(
            "SELECT COUNT(*) as c FROM trust_logs WHERE session_id = ? AND timestamp >= ?",
            (session_id, one_minute_ago)
        ).fetchone()
        requests_per_minute = rate_row["c"] if rate_row else 0

    # Build telemetry dict from keystroke + mouse metrics
    telemetry = {}
    if payload.keystroke_metrics:
        telemetry.update(payload.keystroke_metrics)
    if payload.mouse_metrics:
        telemetry["mouse_straightness"] = payload.mouse_metrics.get("path_straightness", 0)
        telemetry["mouse_avg_velocity"] = payload.mouse_metrics.get("avg_velocity", 0)

    # Build real session context
    session_data = {
        "requests_per_minute": requests_per_minute,
        "duration_minutes": duration_minutes,
        "ip_address": session["ip_address"] if session else "127.0.0.1",
    }

    result = compute_trust_score(
        user_id=user_id,
        session_id=session_id,
        telemetry=telemetry,
        session_data=session_data,
        device_fingerprint=payload.device_fingerprint,
        transaction_amount=payload.transaction_amount,
        current_city=payload.current_city,
    )

    return result
