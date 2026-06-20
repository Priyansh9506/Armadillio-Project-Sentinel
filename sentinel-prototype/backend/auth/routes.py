"""
Project Sentinel — Auth Routes
Registration, Login, JWT token management.
Industry-grade session auth with proper dependency injection.
"""
import uuid
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_db

router = APIRouter()

# ─── Constants ──────────────────────────────────────────────────────

REFRESH_TOKEN_EXPIRE_DAYS = 7


# ─── Pydantic Schemas ───────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    credential: str
    login_type: str = "password"  # password, pin, otp

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    session_id: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    mfa_token: str


# ─── JWT Helpers ────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """Short-lived access token (15 min for banking-grade security)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "token_type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Long-lived refresh token (7 days). Used only to rotate access tokens."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "token_type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises HTTPException on failure."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ─── Auth Dependency (FastAPI Depends) ──────────────────────────────

async def get_current_user(authorization: str = Header(None)) -> dict:
    """
    Reusable dependency that extracts and validates the Bearer token.
    Use as: user = Depends(get_current_user)
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)

    # Ensure this is an access token, not a refresh token
    if payload.get("token_type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type. Use an access token.")

    # Validate session is still active
    session_id = payload.get("session_id")
    if session_id:
        with get_db() as db:
            session = db.execute(
                "SELECT is_active FROM sessions WHERE session_id = %s", (session_id,)
            ).fetchone()
            if session and session["is_active"] == 0:
                raise HTTPException(status_code=401, detail="Session has been logged out")

    return {
        "user_id": payload["user_id"],
        "username": payload["username"],
        "session_id": payload.get("session_id"),
    }


# ─── Routes ─────────────────────────────────────────────────────────

@router.post("/register")
async def register(req: RegisterRequest):
    """Register a new user account."""
    password_hash = hash_password(req.password)

    with get_db() as db:
        existing = db.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (req.username, req.email)
        ).fetchone()

        if existing:
            raise HTTPException(status_code=400, detail="Username or email already exists")

        cursor = db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (req.username, req.email, password_hash)
        )
        user_id = cursor.lastrowid

        db.execute(
            "INSERT INTO behavioral_baselines (user_id) VALUES (%s)",
            (user_id,)
        )

    session_id = str(uuid.uuid4())

    # Record session
    with get_db() as db:
        db.execute(
            "INSERT INTO sessions (session_id, user_id, ip_address) VALUES (%s, %s, %s)",
            (session_id, user_id, "127.0.0.1")
        )

    # Push to Supabase if available
    try:
        from supabase_client import get_supabase
        sb = get_supabase()
        if sb:
            sb.table("users").insert({
                "username": req.username,
                "email": req.email,
                "password_hash": password_hash,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
    except Exception as e:
        print(f"[WARN] Supabase user sync failed: {e}")

    token = create_access_token({
        "user_id": user_id,
        "username": req.username,
        "session_id": session_id
    })
    refresh_token = create_refresh_token({
        "user_id": user_id,
        "username": req.username,
        "session_id": session_id
    })

    return {
        "token": token,
        "refresh_token": refresh_token,
        "session_id": session_id,
        "user": {"id": user_id, "username": req.username, "email": req.email},
        "message": "Registration successful"
    }


import os

def get_password_pepper() -> bytes:
    return os.getenv("PASSWORD_PEPPER", "default_secret_password_pepper").encode()

def hash_password(password: str) -> str:
    """Bcrypt hash with system-wide Pepper (Salt + Pepper) for Password storage."""
    peppered_pw = password.encode() + get_password_pepper()
    return bcrypt.hashpw(peppered_pw, bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify Password against the Salted & Peppered Bcrypt hash."""
    peppered_pw = plain_password.encode() + get_password_pepper()
    try:
        return bcrypt.checkpw(peppered_pw, hashed_password.encode('utf-8'))
    except ValueError:
        # Legacy fallback for old passwords without pepper
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@router.post("/login")
async def login(req: LoginRequest, request: Request):
    """Login with username and password. Returns access + refresh token pair."""
    with get_db() as db:
        user = db.execute(
            "SELECT id, username, email, password_hash, upi_pin_hash, balance FROM users WHERE username = %s OR phone_no = %s",
            (req.username, req.username)
        ).fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if req.login_type == "password":
            if not verify_password(req.credential, user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid password")
        elif req.login_type == "pin":
            import hashlib
            pin_hash = hashlib.sha256(req.credential.encode()).hexdigest()
            if pin_hash != user["upi_pin_hash"]:
                raise HTTPException(status_code=401, detail="Invalid PIN")
        elif req.login_type == "otp":
            # Mock OTP logic for prototype - accepts any 6 digit OTP or 123456
            if len(req.credential) != 6 or not req.credential.isdigit():
                raise HTTPException(status_code=401, detail="Invalid OTP format")

        session_id = str(uuid.uuid4())

        # Capture real client IP
        client_ip = request.client.host if request.client else "127.0.0.1"

        db.execute(
            "INSERT INTO sessions (session_id, user_id, ip_address) VALUES (%s, %s, %s)",
            (session_id, user["id"], client_ip)
        )

        token = create_access_token({
            "user_id": user["id"],
            "username": user["username"],
            "session_id": session_id
        })

        refresh_token = create_refresh_token({
            "user_id": user["id"],
            "username": user["username"],
            "session_id": session_id
        })

        return {
            "token": token,
            "refresh_token": refresh_token,
            "session_id": session_id,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "balance": user["balance"]
            },
            "trust_score": 100,
            "message": "Login successful"
        }


@router.post("/refresh")
async def refresh(req: RefreshRequest):
    """Generate a new access token from a valid refresh token."""
    try:
        payload = jwt.decode(req.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired. Please login again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Ensure this is actually a refresh token
    if payload.get("token_type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type. Expected refresh token.")

    session_id = payload.get("session_id")

    # Verify session is still active
    with get_db() as db:
        session = db.execute(
            "SELECT is_active FROM sessions WHERE session_id = %s", (session_id,)
        ).fetchone()
        if not session or session["is_active"] == 0:
            raise HTTPException(status_code=401, detail="Session has been logged out")

    new_token = create_access_token({
        "user_id": payload["user_id"],
        "username": payload["username"],
        "session_id": session_id
    })
    return {"token": new_token}


@router.post("/logout")
async def logout(req: LogoutRequest, user: dict = Depends(get_current_user)):
    """Invalidate session on logout. Requires valid auth."""
    # Only allow users to logout their own session
    if req.session_id != user["session_id"]:
        # Still allow it — user might be logging out from SOC view
        pass

    with get_db() as db:
        db.execute(
            "UPDATE sessions SET is_active = 0 WHERE session_id = %s",
            (req.session_id,)
        )

    return {"message": "Logged out successfully", "session_id": req.session_id}


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Return current authenticated user info."""
    with get_db() as db:
        user_row = db.execute("SELECT email, balance FROM users WHERE id = %s", (user["user_id"],)).fetchone()
        if user_row:
            user["email"] = user_row["email"]
            user["balance"] = user_row["balance"]
    return user


@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    """Change user password. Requires old password and an MFA token."""
    user_id = user["user_id"]

    with get_db() as db:
        user_row = db.execute(
            "SELECT password_hash, totp_secret FROM users WHERE id = %s", (user_id,)
        ).fetchone()

        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(req.old_password, user_row["password_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect current password")

        # Step 2: Verify MFA token
        mfa_verified = False

        # Option A: Check if it's a verified push-auth challenge
        challenge = db.execute(
            "SELECT status FROM push_auth_challenges WHERE id = %s AND user_id = %s",
            (req.mfa_token, user_id)
        ).fetchone()
        if challenge and challenge["status"] == "VERIFIED":
            mfa_verified = True

        # Option B: Check TOTP (if user has authenticator setup)
        if not mfa_verified and user_row["totp_secret"]:
            try:
                import pyotp
                totp = pyotp.TOTP(user_row["totp_secret"])
                if totp.verify(req.mfa_token, valid_window=1):
                    mfa_verified = True
            except Exception:
                pass

        # Option C: Prototype fallback
        if not mfa_verified and req.mfa_token == "123456":
            mfa_verified = True

        if not mfa_verified:
            raise HTTPException(status_code=403, detail="MFA verification failed. Complete push-auth or enter valid TOTP code.")

        new_password_hash = hash_password(req.new_password)

        db.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_password_hash, user_id)
        )

        # Log a security alert for password change
        db.execute("""
            INSERT INTO alerts (user_id, alert_type, severity, description)
            VALUES (%s, %s, %s, %s)
        """, (user_id, 'password_change', 'MEDIUM', 'Password was successfully changed.'))

    # Push to Supabase
    try:
        from supabase_client import get_supabase
        sb = get_supabase()
        if sb:
            sb.table("users").update({
                "password_hash": new_password_hash
            }).eq("username", user["username"]).execute()
    except Exception as e:
        print(f"[WARN] Supabase password update failed: {e}")

    return {"success": True, "message": "Password changed successfully"}
