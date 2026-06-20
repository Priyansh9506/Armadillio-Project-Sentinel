"""
Project Sentinel — MFA Routes
Push Auth (number matching via WebSocket), Voice Liveness, and Duress Transfer.
Uses shared auth dependency for all protected endpoints.
"""
import uuid
import random
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional

from auth.routes import get_current_user
from config import DURESS_PIN_SUFFIX
from database import get_db

router = APIRouter()

# In-memory store for active WebSocket connections (per user)
# In production this would use Redis Pub/Sub
active_connections: dict[int, list[WebSocket]] = {}


class PushAuthRequest(BaseModel):
    session_id: str

class PushAuthVerify(BaseModel):
    challenge_id: str
    selected_number: int

class VoiceLivenessVerify(BaseModel):
    session_id: str
    transcript: str

class DuressTransferRequest(BaseModel):
    session_id: str
    to_account: str
    amount: float
    pin: str


# ─── Push Auth (Number Matching) ────────────────────────────────────

@router.post("/push-auth/initiate")
async def initiate_push_auth(req: PushAuthRequest, user: dict = Depends(get_current_user)):
    """
    Initiates a push auth challenge.
    Generates 3 numbers, one correct. Sends to trusted device via WebSocket.
    Returns the correct number to the challenging device.
    """
    user_id = user["user_id"]

    # Generate challenge
    correct_number = random.randint(10, 99)
    decoys = set()
    while len(decoys) < 2:
        d = random.randint(10, 99)
        if d != correct_number:
            decoys.add(d)

    options = sorted(list(decoys) + [correct_number])
    challenge_id = str(uuid.uuid4())

    # Store challenge in DB
    with get_db() as db:
        db.execute("""
            INSERT INTO push_auth_challenges (id, session_id, user_id, correct_number, status)
            VALUES (%s, %s, %s, %s, 'PENDING')
        """, (challenge_id, req.session_id, user_id, correct_number))

    # Send to trusted device via WebSocket
    if user_id in active_connections:
        message = json.dumps({
            "type": "PUSH_AUTH_CHALLENGE",
            "challenge_id": challenge_id,
            "options": options,
            "message": "Login attempt detected. Select the matching number.",
        })
        for ws in active_connections[user_id]:
            try:
                await ws.send_text(message)
            except Exception:
                pass

    return {
        "challenge_id": challenge_id,
        "correct_number": correct_number,
        "message": "Verify on your trusted device"
    }


@router.post("/push-auth/verify")
async def verify_push_auth(req: PushAuthVerify, user: dict = Depends(get_current_user)):
    """Verify the number selected on the trusted device."""
    user_id = user["user_id"]

    with get_db() as db:
        challenge = db.execute(
            "SELECT * FROM push_auth_challenges WHERE id = %s AND user_id = %s",
            (req.challenge_id, user_id)
        ).fetchone()

        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")

        if challenge["status"] != "PENDING":
            raise HTTPException(status_code=400, detail="Challenge already resolved")

        if req.selected_number == challenge["correct_number"]:
            db.execute(
                "UPDATE push_auth_challenges SET status = 'VERIFIED' WHERE id = %s",
                (req.challenge_id,)
            )

            # Notify the laptop session via WebSocket
            if user_id in active_connections:
                msg = json.dumps({"type": "PUSH_AUTH_VERIFIED", "challenge_id": req.challenge_id})
                for ws in active_connections[user_id]:
                    try:
                        await ws.send_text(msg)
                    except Exception:
                        pass

            return {"verified": True, "message": "Identity verified successfully"}
        else:
            db.execute(
                "UPDATE push_auth_challenges SET status = 'FAILED' WHERE id = %s",
                (req.challenge_id,)
            )
            return {"verified": False, "message": "Incorrect number selected"}


# ─── Voice Liveness ─────────────────────────────────────────────────

LIVENESS_PHRASES = [
    "blue apple quiet river",
    "green mountain silver moon",
    "red ocean golden sunrise",
    "white forest crystal lake",
]

@router.get("/voice-liveness/phrase")
async def get_liveness_phrase():
    """Returns a random phrase the user must read aloud."""
    phrase = random.choice(LIVENESS_PHRASES)
    return {"phrase": phrase}


@router.post("/voice-liveness/verify")
async def verify_voice_liveness(req: VoiceLivenessVerify):
    """
    Verify the user's spoken transcript matches the expected phrase.
    Uses simple string similarity — the point is the UX flow.
    """
    transcript = req.transcript.lower().strip()

    for phrase in LIVENESS_PHRASES:
        phrase_words = set(phrase.split())
        transcript_words = set(transcript.split())
        overlap = len(phrase_words & transcript_words)
        if overlap >= len(phrase_words) * 0.6:
            return {"verified": True, "message": "Voice liveness confirmed"}

    return {"verified": False, "message": "Phrase did not match. Please try again."}


# ─── Invisible Panic Button (Duress Transfer) ──────────────────────

@router.post("/duress-transfer")
async def duress_transfer(req: DuressTransferRequest, user: dict = Depends(get_current_user)):
    """
    If the user's PIN ends with the duress suffix, the transfer looks successful
    but actually routes to a holding account and triggers a silent alarm.
    """
    user_id = user["user_id"]
    username = user["username"]

    is_duress = req.pin.endswith(DURESS_PIN_SUFFIX)

    with get_db() as db:
        if is_duress:
            # ── DURESS MODE ──
            db.execute("""
                INSERT INTO transactions (user_id, amount, merchant, category, is_duress)
                VALUES (%s, %s, %s, %s, 1)
            """, (user_id, req.amount, f"HELD_FOR_{req.to_account}", "DURESS_HOLD"))

            # Trigger CRITICAL silent alarm
            db.execute("""
                INSERT INTO alerts (user_id, alert_type, severity, description)
                VALUES (%s, %s, %s, %s)
            """, (user_id, "DURESS_TRANSFER", "CRITICAL",
                  f"DURESS ALERT: User {username} attempted transfer of ₹{req.amount:,.0f} "
                  f"to {req.to_account} under coercion. Funds held in secure account. "
                  f"GPS coordinates should be captured."))

            # Return SUCCESS to fool the attacker — no _duress_triggered leak
            return {
                "success": True,
                "message": f"₹{req.amount:,.2f} transferred successfully to {req.to_account}",
                "transaction_id": f"TXN_{uuid.uuid4().hex[:8].upper()}",
            }
        else:
            # Normal transfer
            db.execute("""
                INSERT INTO transactions (user_id, amount, merchant, category)
                VALUES (%s, %s, %s, %s)
            """, (user_id, req.amount, req.to_account, "TRANSFER"))

            return {
                "success": True,
                "message": f"₹{req.amount:,.2f} transferred successfully to {req.to_account}",
                "transaction_id": f"TXN_{uuid.uuid4().hex[:8].upper()}"
            }


# ─── WebSocket for Push Auth Notifications ──────────────────────────

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    WebSocket connection for real-time push auth notifications.
    The "trusted mobile device" connects here to receive challenges.
    """
    await websocket.accept()

    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "PUSH_AUTH_RESPONSE":
                challenge_id = message.get("challenge_id")
                selected = message.get("selected_number")

                with get_db() as db:
                    challenge = db.execute(
                        "SELECT * FROM push_auth_challenges WHERE id = %s",
                        (challenge_id,)
                    ).fetchone()

                    if challenge and challenge["status"] == "PENDING":
                        if selected == challenge["correct_number"]:
                            db.execute(
                                "UPDATE push_auth_challenges SET status = 'VERIFIED' WHERE id = %s",
                                (challenge_id,)
                            )
                            for ws in active_connections.get(user_id, []):
                                try:
                                    await ws.send_text(json.dumps({
                                        "type": "PUSH_AUTH_VERIFIED",
                                        "challenge_id": challenge_id
                                    }))
                                except Exception:
                                    pass
                        else:
                            db.execute(
                                "UPDATE push_auth_challenges SET status = 'FAILED' WHERE id = %s",
                                (challenge_id,)
                            )
                            await websocket.send_text(json.dumps({
                                "type": "PUSH_AUTH_FAILED",
                                "challenge_id": challenge_id
                            }))

    except WebSocketDisconnect:
        if user_id in active_connections:
            active_connections[user_id].remove(websocket)
            if not active_connections[user_id]:
                del active_connections[user_id]
