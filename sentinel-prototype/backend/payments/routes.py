"""
Project Sentinel — Payment Routes
Full UPI/NEFT payment processing with UPI PIN, PIN change with MFA.
Stores transactions in Supabase (cloud) + local SQLite (SOC dashboard).
"""
import uuid
import hashlib
import secrets
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from auth.routes import get_current_user
from database import get_db
from config import DURESS_PIN_SUFFIX

router = APIRouter()


# ─── Pydantic Models ────────────────────────────────────────────────

class SetUPIPinRequest(BaseModel):
    new_pin: str  # 4 or 6 digit

class UPIPaymentRequest(BaseModel):
    session_id: str
    to_upi_id: str
    amount: float
    note: Optional[str] = ""
    upi_pin: str

class BankTransferRequest(BaseModel):
    session_id: str
    to_account: str
    ifsc_code: str
    amount: float
    note: Optional[str] = ""
    txn_pin: str

class BillPayRequest(BaseModel):
    session_id: str
    biller_id: str
    amount: float
    txn_pin: str

class ChangeUPIPinRequest(BaseModel):
    old_pin: str
    new_pin: str
    mfa_token: str  # challenge_id from push-auth or TOTP code


# ─── Helpers ─────────────────────────────────────────────────────────

def hash_pin(pin: str) -> str:
    """SHA-256 hash for UPI PIN storage."""
    return hashlib.sha256(pin.encode()).hexdigest()


def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """Verify a plain PIN against stored hash."""
    return hash_pin(plain_pin) == hashed_pin


def _insert_supabase_txn(txn_data: dict):
    """Insert transaction into Supabase. Non-blocking, won't crash if Supabase is down."""
    try:
        from supabase_client import get_supabase
        sb = get_supabase()
        if sb:
            sb.table("transactions").insert(txn_data).execute()
    except Exception as e:
        print(f"[WARN] Supabase insert failed (continuing): {e}")


def _insert_local_txn(user_id: int, amount: float, merchant: str, category: str, is_duress: int = 0):
    """Insert into local SQLite for SOC dashboard."""
    with get_db() as db:
        db.execute("""
            INSERT INTO transactions (user_id, amount, merchant, category, is_duress)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, amount, merchant, category, is_duress))


def _insert_alert(user_id: int, alert_type: str, severity: str, description: str):
    """Insert alert into local DB for SOC dashboard."""
    with get_db() as db:
        db.execute("""
            INSERT INTO alerts (user_id, alert_type, severity, description)
            VALUES (?, ?, ?, ?)
        """, (user_id, alert_type, severity, description))


# ─── Set UPI PIN (First time setup) ─────────────────────────────────

@router.post("/set-upi-pin")
async def set_upi_pin(req: SetUPIPinRequest, user: dict = Depends(get_current_user)):
    """Set UPI PIN for the first time. PIN must be 4 or 6 digits."""
    if len(req.new_pin) not in (4, 6) or not req.new_pin.isdigit():
        raise HTTPException(status_code=400, detail="UPI PIN must be 4 or 6 digits")

    user_id = user["user_id"]
    pin_hash = hash_pin(req.new_pin)

    with get_db() as db:
        # Check if PIN already set
        existing = db.execute("SELECT upi_pin_hash FROM users WHERE id = ?", (user_id,)).fetchone()
        if existing and existing["upi_pin_hash"]:
            raise HTTPException(status_code=400, detail="UPI PIN already set. Use change-pin endpoint.")

        db.execute("UPDATE users SET upi_pin_hash = ? WHERE id = ?", (pin_hash, user_id))

    return {"success": True, "message": "UPI PIN set successfully"}


# ─── UPI Payment ─────────────────────────────────────────────────────

@router.post("/upi/send")
async def upi_send(req: UPIPaymentRequest, user: dict = Depends(get_current_user)):
    """
    Send money via UPI. Requires valid UPI PIN.
    If PIN ends with duress suffix (9999), triggers silent alarm.
    """
    user_id = user["user_id"]
    username = user["username"]

    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # Verify UPI PIN
    with get_db() as db:
        row = db.execute("SELECT upi_pin_hash FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row or not row["upi_pin_hash"]:
            raise HTTPException(status_code=400, detail="UPI PIN not set. Please set your PIN first.")

        # Check for duress suffix BEFORE verifying
        is_duress = req.upi_pin.endswith(DURESS_PIN_SUFFIX)
        actual_pin = req.upi_pin[:-len(DURESS_PIN_SUFFIX)] if is_duress else req.upi_pin

        if not verify_pin(actual_pin, row["upi_pin_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect UPI PIN")

    txn_id = f"UPI{uuid.uuid4().hex[:10].upper()}"
    now = datetime.utcnow().isoformat()

    if is_duress:
        # DURESS MODE — looks successful but funds held + silent alarm
        _insert_local_txn(user_id, req.amount, f"HELD_FOR_{req.to_upi_id}", "DURESS_HOLD", 1)
        _insert_alert(user_id, "DURESS_UPI_PAYMENT", "CRITICAL",
            f"DURESS: User {username} sent ₹{req.amount:,.0f} to {req.to_upi_id} under coercion. "
            f"Funds routed to holding account. Note: '{req.note}'")

        _insert_supabase_txn({
            "txn_id": txn_id, "from_user": username, "to_upi_id": req.to_upi_id,
            "amount": req.amount, "note": req.note or "", "type": "UPI",
            "status": "DURESS_HELD", "is_duress": True, "created_at": now
        })

        return {
            "success": True,
            "message": f"₹{req.amount:,.2f} sent to {req.to_upi_id}",
            "transaction_id": txn_id,
            "note": req.note
        }
    else:
        # Normal payment
        _insert_local_txn(user_id, req.amount, req.to_upi_id, "UPI_PAYMENT", 0)

        _insert_supabase_txn({
            "txn_id": txn_id, "from_user": username, "to_upi_id": req.to_upi_id,
            "amount": req.amount, "note": req.note or "", "type": "UPI",
            "status": "SUCCESS", "is_duress": False, "created_at": now
        })

        return {
            "success": True,
            "message": f"₹{req.amount:,.2f} sent to {req.to_upi_id}",
            "transaction_id": txn_id,
            "note": req.note
        }


# ─── NEFT/IMPS Transfer ─────────────────────────────────────────────

@router.post("/transfer/neft")
async def neft_transfer(req: BankTransferRequest, user: dict = Depends(get_current_user)):
    """Bank-to-bank NEFT/IMPS transfer with transaction PIN."""
    user_id = user["user_id"]
    username = user["username"]

    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    with get_db() as db:
        row = db.execute("SELECT upi_pin_hash FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row or not row["upi_pin_hash"]:
            raise HTTPException(status_code=400, detail="Transaction PIN not set.")

        is_duress = req.txn_pin.endswith(DURESS_PIN_SUFFIX)
        actual_pin = req.txn_pin[:-len(DURESS_PIN_SUFFIX)] if is_duress else req.txn_pin

        if not verify_pin(actual_pin, row["upi_pin_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect Transaction PIN")

    txn_id = f"NEFT{uuid.uuid4().hex[:10].upper()}"
    now = datetime.utcnow().isoformat()

    if is_duress:
        _insert_local_txn(user_id, req.amount, f"HELD_FOR_{req.to_account}", "DURESS_HOLD", 1)
        _insert_alert(user_id, "DURESS_NEFT", "CRITICAL",
            f"DURESS: User {username} NEFT ₹{req.amount:,.0f} to A/C {req.to_account} "
            f"(IFSC: {req.ifsc_code}) under coercion. Funds held.")

        _insert_supabase_txn({
            "txn_id": txn_id, "from_user": username, "to_account": req.to_account,
            "ifsc_code": req.ifsc_code, "amount": req.amount, "note": req.note or "",
            "type": "NEFT", "status": "DURESS_HELD", "is_duress": True, "created_at": now
        })
    else:
        _insert_local_txn(user_id, req.amount, req.to_account, "NEFT_TRANSFER", 0)

        _insert_supabase_txn({
            "txn_id": txn_id, "from_user": username, "to_account": req.to_account,
            "ifsc_code": req.ifsc_code, "amount": req.amount, "note": req.note or "",
            "type": "NEFT", "status": "SUCCESS", "is_duress": False, "created_at": now
        })

    return {
        "success": True,
        "message": f"₹{req.amount:,.2f} transferred to A/C {req.to_account}",
        "transaction_id": txn_id
    }


# ─── Bill Payment ────────────────────────────────────────────────────

@router.post("/bills/pay")
async def pay_bill(req: BillPayRequest, user: dict = Depends(get_current_user)):
    """Pay a utility bill."""
    user_id = user["user_id"]
    username = user["username"]

    with get_db() as db:
        row = db.execute("SELECT upi_pin_hash FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row or not row["upi_pin_hash"]:
            raise HTTPException(status_code=400, detail="Transaction PIN not set.")

        is_duress = req.txn_pin.endswith(DURESS_PIN_SUFFIX)
        actual_pin = req.txn_pin[:-len(DURESS_PIN_SUFFIX)] if is_duress else req.txn_pin

        if not verify_pin(actual_pin, row["upi_pin_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect Transaction PIN")

    txn_id = f"BILL{uuid.uuid4().hex[:10].upper()}"
    now = datetime.utcnow().isoformat()

    _insert_local_txn(user_id, req.amount, req.biller_id, "BILL_PAYMENT", 1 if is_duress else 0)

    _insert_supabase_txn({
        "txn_id": txn_id, "from_user": username, "biller_id": req.biller_id,
        "amount": req.amount, "type": "BILL", "status": "DURESS_HELD" if is_duress else "SUCCESS",
        "is_duress": is_duress, "created_at": now
    })

    if is_duress:
        _insert_alert(user_id, "DURESS_BILL", "CRITICAL",
            f"DURESS: User {username} bill payment ₹{req.amount:,.0f} to {req.biller_id} under coercion.")

    return {
        "success": True,
        "message": f"Bill of ₹{req.amount:,.2f} paid to {req.biller_id}",
        "transaction_id": txn_id
    }


# ─── Change UPI PIN (Requires Old PIN + MFA) ────────────────────────

@router.post("/change-upi-pin")
async def change_upi_pin(req: ChangeUPIPinRequest, user: dict = Depends(get_current_user)):
    """
    Change UPI PIN. Requires:
    1. Correct old PIN
    2. Valid MFA token (push-auth challenge_id verified, or valid TOTP code)
    """
    user_id = user["user_id"]

    if len(req.new_pin) not in (4, 6) or not req.new_pin.isdigit():
        raise HTTPException(status_code=400, detail="New PIN must be 4 or 6 digits")

    if req.old_pin == req.new_pin:
        raise HTTPException(status_code=400, detail="New PIN must be different from old PIN")

    with get_db() as db:
        row = db.execute("SELECT upi_pin_hash, totp_secret FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row or not row["upi_pin_hash"]:
            raise HTTPException(status_code=400, detail="UPI PIN not set yet. Use set-pin first.")

        # Step 1: Verify old PIN
        if not verify_pin(req.old_pin, row["upi_pin_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect old PIN")

        # Step 2: Verify MFA token
        mfa_verified = False

        # Option A: Check if it's a verified push-auth challenge
        challenge = db.execute(
            "SELECT status FROM push_auth_challenges WHERE id = ? AND user_id = ?",
            (req.mfa_token, user_id)
        ).fetchone()
        if challenge and challenge["status"] == "VERIFIED":
            mfa_verified = True

        # Option B: Check TOTP (if user has authenticator setup)
        if not mfa_verified and row["totp_secret"]:
            try:
                import pyotp
                totp = pyotp.TOTP(row["totp_secret"])
                if totp.verify(req.mfa_token, valid_window=1):
                    mfa_verified = True
            except Exception:
                pass

        if not mfa_verified:
            raise HTTPException(status_code=403, detail="MFA verification failed. Complete push-auth or enter valid TOTP code.")

        # Step 3: Update PIN
        new_hash = hash_pin(req.new_pin)
        db.execute("UPDATE users SET upi_pin_hash = ? WHERE id = ?", (new_hash, user_id))

        # Log the PIN change
        db.execute("""
            INSERT INTO alerts (user_id, alert_type, severity, description)
            VALUES (?, 'UPI_PIN_CHANGED', 'INFO', ?)
        """, (user_id, f"UPI PIN changed successfully via MFA for user {user['username']}"))

    return {"success": True, "message": "UPI PIN changed successfully"}


# ─── Get Transaction History ─────────────────────────────────────────

@router.get("/transactions")
async def get_transactions(user: dict = Depends(get_current_user)):
    """Fetch recent transactions for the logged-in user."""
    user_id = user["user_id"]

    with get_db() as db:
        rows = db.execute("""
            SELECT id, amount, merchant, category, is_duress, timestamp
            FROM transactions WHERE user_id = ?
            ORDER BY timestamp DESC LIMIT 20
        """, (user_id,)).fetchall()

    return {
        "transactions": [
            {
                "id": r["id"], "amount": r["amount"], "merchant": r["merchant"],
                "category": r["category"], "is_duress": bool(r["is_duress"]),
                "timestamp": r["timestamp"]
            }
            for r in rows
        ]
    }


# ─── Check if UPI PIN is set ─────────────────────────────────────────

@router.get("/pin-status")
async def pin_status(user: dict = Depends(get_current_user)):
    """Check if UPI PIN has been set for the current user."""
    user_id = user["user_id"]

    with get_db() as db:
        row = db.execute("SELECT upi_pin_hash FROM users WHERE id = ?", (user_id,)).fetchone()

    has_pin = bool(row and row["upi_pin_hash"])
    return {"has_pin": has_pin}
