"""
Project Sentinel — SOC Dashboard API Routes
Serves alerts, trust logs, active sessions, and fraud graph data.
All endpoints protected via auth dependency.
"""
from fastapi import APIRouter, Query, Depends
from database import get_db
from datetime import datetime, timezone, timedelta
from auth.routes import get_current_user

router = APIRouter()


def format_ist(timestamp_str):
    """Convert UTC timestamp string to IST (UTC+05:30) for display."""
    if not timestamp_str:
        return timestamp_str
    try:
        dt = datetime.strptime(str(timestamp_str).split('.')[0], "%Y-%m-%d %H:%M:%S")
        dt_utc = dt.replace(tzinfo=timezone.utc)
        ist_offset = timezone(timedelta(hours=5, minutes=30))
        dt_ist = dt_utc.astimezone(ist_offset)
        return dt_ist.strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception:
        return str(timestamp_str)


@router.get("/alerts")
async def get_alerts(limit: int = Query(20, le=100), user: dict = Depends(get_current_user)):
    """Get recent security alerts for the SOC dashboard."""
    with get_db() as db:
        alerts = db.execute("""
            SELECT a.*, u.username
            FROM alerts a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
            LIMIT %s
        """, (limit,)).fetchall()

    res = []
    for a in alerts:
        d = dict(a)
        d["timestamp"] = format_ist(d.get("timestamp"))
        res.append(d)
    return res


@router.get("/trust-logs")
async def get_trust_logs(user_id: int = None, limit: int = Query(50, le=200), user: dict = Depends(get_current_user)):
    """Get trust score history."""
    with get_db() as db:
        if user_id:
            logs = db.execute("""
                SELECT * FROM trust_logs
                WHERE user_id = %s
                ORDER BY timestamp DESC LIMIT %s
            """, (user_id, limit)).fetchall()
        else:
            logs = db.execute("""
                SELECT tl.*, u.username
                FROM trust_logs tl
                LEFT JOIN users u ON tl.user_id = u.id
                ORDER BY tl.timestamp DESC LIMIT %s
            """, (limit,)).fetchall()

    res = []
    for l in logs:
        d = dict(l)
        d["timestamp"] = format_ist(d.get("timestamp"))
        res.append(d)
    return res


@router.get("/sessions")
async def get_active_sessions(user: dict = Depends(get_current_user)):
    """Get all active sessions with their latest trust scores."""
    with get_db() as db:
        sessions = db.execute("""
            SELECT s.*, u.username,
                   (SELECT trust_score FROM trust_logs
                    WHERE session_id = s.session_id
                    ORDER BY timestamp DESC LIMIT 1) as latest_trust_score,
                   (SELECT decision FROM trust_logs
                    WHERE session_id = s.session_id
                    ORDER BY timestamp DESC LIMIT 1) as latest_decision
            FROM sessions s
            LEFT JOIN users u ON s.user_id = u.id
            WHERE s.is_active = 1
            ORDER BY s.start_time DESC
        """).fetchall()

    res = []
    for s in sessions:
        d = dict(s)
        d["start_time"] = format_ist(d.get("start_time"))
        d["last_activity"] = format_ist(d.get("last_activity"))
        res.append(d)
    return res


@router.get("/stats")
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    """Get aggregate stats for the SOC dashboard."""
    with get_db() as db:
        total_users = db.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
        active_sessions = db.execute("SELECT COUNT(*) as c FROM sessions WHERE is_active = 1").fetchone()["c"]
        critical_alerts = db.execute(
            "SELECT COUNT(*) as c FROM alerts WHERE severity = 'CRITICAL' AND resolved = 0"
        ).fetchone()["c"]
        total_alerts = db.execute(
            "SELECT COUNT(*) as c FROM alerts WHERE resolved = 0"
        ).fetchone()["c"]
        duress_count = db.execute(
            "SELECT COUNT(*) as c FROM transactions WHERE is_duress = 1"
        ).fetchone()["c"]

    return {
        "total_users": total_users,
        "active_sessions": active_sessions,
        "critical_alerts": critical_alerts,
        "total_alerts": total_alerts,
        "duress_transfers": duress_count,
    }
