"""
Project Sentinel — Trust Engine: Device Scoring
Compares current browser fingerprint against known user devices.
"""


def compute_device_score(fingerprint: dict, known_fingerprints: list) -> float:
    """
    Score how likely this device belongs to the legitimate user.
    Returns 0-100.
    """
    score = 0

    fp_hash = fingerprint.get("hash", "")

    # Known device = strong trust signal
    if fp_hash and fp_hash in known_fingerprints:
        score += 50

    # Expected timezone
    if fingerprint.get("timezone") == "Asia/Kolkata":
        score += 15

    # Known platform
    if fingerprint.get("platform", "").startswith("Win"):
        score += 20

    # Known screen resolution
    if fingerprint.get("screen_resolution") in ["1920x1080", "1366x768", "2560x1440"]:
        score += 10

    # Touch support mismatch (desktop claiming touch = suspicious)
    if fingerprint.get("touch_support") is True and fingerprint.get("platform", "").startswith("Win"):
        score -= 10

    return min(max(score, 0), 100)
