"""
Project Sentinel — Trust Engine: Behavioral Scoring
Compares current typing/mouse behavior against the user's enrolled baseline.
"""
import numpy as np


def compute_behavioral_score(current: dict, baseline: dict) -> float:
    """
    Compare current telemetry metrics against stored baseline.
    Returns 0-100 score. 100 = perfectly matches baseline (same user).
    
    Uses z-score comparison — no ML training needed for the prototype.
    """
    score = 100.0

    current_flight = current.get("avg_flight_time") or 0.0
    b_flight = baseline.get("avg_flight_time") or 0.0
    b_std_flight = baseline.get("std_flight_time") or 0.0
    # Only penalize if user is actually typing (current_flight > 0)
    if b_flight > 0 and b_std_flight > 0 and current_flight > 0:
        flight_z = abs(current_flight - b_flight) / max(b_std_flight, 1)
        score -= min(flight_z * 10, 30)

    # ── Keystroke Dwell Time ──
    current_dwell = current.get("avg_dwell_time") or 0.0
    b_dwell = baseline.get("avg_dwell_time") or 0.0
    b_std_dwell = baseline.get("std_dwell_time") or 0.0
    if b_dwell > 0 and b_std_dwell > 0 and current_dwell > 0:
        dwell_z = abs(current_dwell - b_dwell) / max(b_std_dwell, 1)
        score -= min(dwell_z * 10, 25)

    # ── Typing Speed ──
    current_speed = current.get("typing_speed") or 0.0
    b_speed = baseline.get("avg_typing_speed") or 0.0
    if b_speed > 0 and current_speed > 0:
        speed_ratio = current_speed / max(b_speed, 0.1)
        if speed_ratio > 1.3 or speed_ratio < 0.7:
            score -= 20

    # ── Mouse Straightness (Bot Detection) ──
    if (current.get("mouse_straightness") or 0.0) > 0.95:
        score -= 15

    return max(score, 0)


def update_baseline(user_id: int, metrics: dict, db_conn) -> None:
    """
    Update the user's behavioral baseline with new telemetry data.
    Uses exponential moving average to smooth the baseline over time.
    """
    baseline = db_conn.execute(
        "SELECT * FROM behavioral_baselines WHERE user_id = ?", (user_id,)
    ).fetchone()

    if not baseline:
        return
    baseline = dict(baseline)

    sample_count = baseline.get("sample_count") or 0
    alpha = 0.1 if sample_count > 10 else 0.3  # Learn faster initially

    b_flight = baseline.get("avg_flight_time") or 0.0
    b_dwell = baseline.get("avg_dwell_time") or 0.0
    b_speed = baseline.get("avg_typing_speed") or 0.0
    b_std_flight = baseline.get("std_flight_time") or 0.0
    b_std_dwell = baseline.get("std_dwell_time") or 0.0

    new_avg_flight = _ema(b_flight, metrics.get("avg_flight_time") or 0, alpha)
    new_avg_dwell = _ema(b_dwell, metrics.get("avg_dwell_time") or 0, alpha)
    new_avg_speed = _ema(b_speed, metrics.get("typing_speed") or 0, alpha)

    # Update standard deviations using running calculation
    new_std_flight = _running_std(b_std_flight, b_flight,
                                   metrics.get("avg_flight_time") or 0, sample_count)
    new_std_dwell = _running_std(b_std_dwell, b_dwell,
                                  metrics.get("avg_dwell_time") or 0, sample_count)

    db_conn.execute("""
        UPDATE behavioral_baselines SET
            avg_flight_time = ?,
            avg_dwell_time = ?,
            avg_typing_speed = ?,
            std_flight_time = ?,
            std_dwell_time = ?,
            sample_count = ?
        WHERE user_id = ?
    """, (new_avg_flight, new_avg_dwell, new_avg_speed,
          new_std_flight, new_std_dwell, sample_count + 1, user_id))


def _ema(old_val: float, new_val: float, alpha: float) -> float:
    """Exponential moving average."""
    if old_val == 0:
        return new_val
    return old_val * (1 - alpha) + new_val * alpha


def _running_std(old_std: float, old_mean: float, new_val: float, n: int) -> float:
    """Approximate running standard deviation update."""
    if n < 2:
        return abs(new_val - old_mean) if old_mean > 0 else 0
    deviation = abs(new_val - old_mean)
    return (old_std * (n - 1) + deviation) / n
