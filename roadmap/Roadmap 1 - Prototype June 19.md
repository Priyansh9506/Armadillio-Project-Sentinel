# 🛡️ Project Sentinel — Roadmap 1: Prototype Build

## Deadline: June 19, 2026 (Idea Submission) | Team Armadillo

---

## Timeline Overview

```
NOW (9:00 PM, June 18)
 │
 ├─ Phase 0: Setup & Accounts ─────────── 30 min  (9:00 - 9:30 PM)
 ├─ Phase 1: Backend Foundation ────────── 2 hrs   (9:30 - 11:30 PM)
 ├─ Phase 2: Frontend Login + Dashboard ── 2 hrs   (11:30 PM - 1:30 AM)
 ├─ Phase 3: Telemetry SDK ─────────────── 1.5 hrs (1:30 - 3:00 AM)
 ├─ Phase 4: Trust Score Engine ────────── 1.5 hrs (3:00 - 4:30 AM)
 ├─ Phase 5: Adaptive MFA Flow ─────────── 1.5 hrs (4:30 - 6:00 AM)
 ├─ Phase 6: Neo4j Fraud Graph ─────────── 1.5 hrs (6:00 - 7:30 AM)
 ├─ Phase 7: SOC Dashboard ────────────── 1 hr    (7:30 - 8:30 AM)
 ├─ Phase 8: Polish + Demo Prep ────────── 1.5 hrs (8:30 - 10:00 AM)
 │
 ▼
SUBMISSION READY ✅ (June 19 Morning)
```

---

## What We're Building (Scope Lock)

| ✅ BUILD Tonight                                  | ❌ SKIP (Mention in Report Only)        |
| ------------------------------------------------- | --------------------------------------- |
| Web banking dashboard with live Trust Score gauge | Mobile app (Flutter/React Native)       |
| Keystroke + mouse behavioral telemetry SDK (JS)   | Real ML model training (use heuristics) |
| FastAPI backend with JWT auth                     | Kafka/Redpanda streaming                |
| Heuristic Trust Score Engine (4 sub-scores)       | TensorFlow Lite on-device inference     |
| Adaptive MFA: TOTP + simulated face liveness      | Federated Learning                      |
| Neo4j fraud ring visualization (pre-seeded)       | Zero-Knowledge Proofs                   |
| SOC admin dashboard with alerts                   | RASP / code obfuscation                 |
| Silent Lock blur animation                        | App Attest / Play Integrity             |
| Docker-ready for demo                             | Full UEBA insider threat system         |

---

## Phase 0: Environment & Accounts Setup

**⏱️ 30 minutes | 9:00 - 9:30 PM**

### Step 0.1 — Create Neo4j Aura Free Account

> **YOU do this manually right now while I set up the project.**

1. Open: **https://console.neo4j.io/** (or https://neo4j.com/cloud/aura-free/)
2. Click **"Sign Up"** → use Google account for speed
3. Create a **Free Instance**:
   - Name: `sentinel-fraud-graph`
   - Region: Pick closest (Singapore or Mumbai)
4. **⚠️ SAVE THESE IMMEDIATELY** (they only show once):
   ```
   NEO4J_URI = neo4j+s://xxxxxxxx.databases.neo4j.io
   NEO4J_USERNAME = neo4j
   NEO4J_PASSWORD = xxxxxxxxxxxxxxxxx
   ```
5. Wait ~2 min for status to turn **green (Running)**

### Step 0.2 — Verify Your Machine

Run these in terminal to confirm:

```powershell
python --version      # Need 3.10+
pip --version         # Need pip
node --version        # Need 18+ (for optional tooling)
git --version         # Need git
```

### Step 0.3 — Project Initialization

I will create the full project structure:

```
d:\Hackathon\PSB Hackathon IIT Gandhinagar\sentinel-prototype\
├── backend\
│   ├── main.py                    # FastAPI entry
│   ├── database.py                # SQLite setup
│   ├── config.py                  # Environment variables
│   ├── auth\
│   │   ├── routes.py              # Register / Login / JWT
│   │   └── models.py              # Pydantic schemas
│   ├── telemetry\
│   │   ├── routes.py              # POST /api/telemetry
│   │   └── collector.py           # Process telemetry data
│   ├── trust\
│   │   ├── engine.py              # Composite trust score
│   │   ├── behavioral.py          # Keystroke/mouse scoring
│   │   ├── device.py              # Device fingerprint scoring
│   │   └── session.py             # Session context scoring
│   ├── mfa\
│   │   ├── routes.py              # TOTP verify, face capture
│   │   └── totp_service.py        # pyotp integration
│   ├── graph\
│   │   ├── routes.py              # Neo4j query API
│   │   └── seed_data.py           # Fraud ring seeder
│   └── decision\
│       └── gateway.py             # ALLOW / STEP_UP / BLOCK
├── frontend\
│   ├── index.html                 # Login page
│   ├── dashboard.html             # Banking dashboard
│   ├── soc.html                   # SOC admin dashboard
│   ├── css\
│   │   └── sentinel.css           # Complete design system
│   └── js\
│       ├── telemetry.js           # Keystroke + mouse SDK
│       ├── trust-gauge.js         # Animated trust circle
│       ├── mfa-flow.js            # Step-up MFA UI
│       ├── device-fingerprint.js  # Browser fingerprinting
│       └── app.js                 # Core app logic
├── data\
│   └── seed_fraud_ring.json       # Pre-built fraud network
├── requirements.txt
├── .env                           # Neo4j creds + secrets
├── run.py                         # One-command startup
└── README.md
```

### Step 0.4 — Install Dependencies

```powershell
cd "d:\Hackathon\PSB Hackathon IIT Gandhinagar\sentinel-prototype"
python -m venv venv
.\venv\Scripts\activate
pip install fastapi uvicorn[standard] pyjwt bcrypt pyotp qrcode[pil] neo4j scikit-learn numpy python-multipart aiofiles jinja2
```

**Packages explained:**
| Package | Purpose |
|---|---|
| `fastapi` + `uvicorn` | Backend API server |
| `pyjwt` + `bcrypt` | JWT tokens + password hashing |
| `pyotp` + `qrcode` | TOTP codes + QR for Google Authenticator |
| `neo4j` | Neo4j Aura graph database driver |
| `scikit-learn` + `numpy` | Optional Isolation Forest anomaly detection |
| `python-multipart` | Form data parsing (file uploads) |
| `aiofiles` + `jinja2` | Serve static frontend files |

---

## Phase 1: Backend Foundation

**⏱️ 2 hours | 9:30 - 11:30 PM**

### Step 1.1 — Config & Environment (.env)

```env
# .env file
SECRET_KEY=sentinel-armadillo-secret-key-2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password-here
```

### Step 1.2 — SQLite Database Schema

**Tables to create:**

| Table                  | Purpose                 | Key Columns                                                                        |
| ---------------------- | ----------------------- | ---------------------------------------------------------------------------------- |
| `users`                | User accounts           | id, username, email, password_hash, totp_secret                                    |
| `behavioral_baselines` | Learned typing patterns | user_id, avg_flight_time, avg_dwell_time, std_flight, std_dwell, avg_speed         |
| `trust_logs`           | Every trust score event | user_id, session_id, composite_score, behavioral, device, session, graph, decision |
| `alerts`               | Security events         | user_id, type, severity, description, resolved, timestamp                          |
| `sessions`             | Active sessions         | session_id, user_id, device_fingerprint, ip, start_time, last_activity             |

### Step 1.3 — FastAPI App (main.py)

```python
# Core structure
app = FastAPI(title="Project Sentinel API", version="1.0.0")

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Include routers
app.include_router(auth_router,      prefix="/api/auth",      tags=["Auth"])
app.include_router(telemetry_router, prefix="/api/telemetry", tags=["Telemetry"])
app.include_router(trust_router,     prefix="/api/trust",     tags=["Trust"])
app.include_router(mfa_router,       prefix="/api/mfa",       tags=["MFA"])
app.include_router(graph_router,     prefix="/api/graph",     tags=["Graph"])

# CORS (allow frontend)
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# Serve pages
@app.get("/")         → return login page
@app.get("/dashboard") → return dashboard page
@app.get("/soc")       → return SOC dashboard page
```

### Step 1.4 — Auth Routes (JWT)

**POST `/api/auth/register`**

```json
// Request
{ "username": "priyansh", "email": "p@test.com", "password": "Armadillo2026!" }

// Response
{
  "token": "eyJhbG...",
  "totp_secret": "JBSWY3DPEHPK3PXP",
  "totp_qr_url": "data:image/png;base64,...",
  "message": "Scan QR with Google Authenticator"
}
```

**POST `/api/auth/login`**

```json
// Request
{ "username": "priyansh", "password": "Armadillo2026!" }

// Response
{
  "token": "eyJhbG...",
  "session_id": "uuid-here",
  "trust_score": 95,
  "user": { "id": 1, "username": "priyansh" }
}
```

### Step 1.5 — JWT Token Middleware

Every subsequent request must include:

```
Authorization: Bearer <jwt-token>
```

Middleware extracts `user_id` and `session_id` and injects into all route handlers.

---

## Phase 2: Frontend — Login + Banking Dashboard

**⏱️ 2 hours | 11:30 PM - 1:30 AM**

### Step 2.1 — Design System (sentinel.css)

**Color Palette:**

```css
:root {
  --primary: #ff6b35; /* BoB Orange */
  --accent: #00d4aa; /* Trust Green */
  --warning: #ffb800; /* Amber */
  --danger: #ff3b5c; /* Alert Red */
  --bg-dark: #0a0e27; /* Deep Navy */
  --bg-surface: #141832; /* Card surface */
  --bg-glass: rgba(20, 24, 50, 0.8);
  --text-primary: #ffffff;
  --text-muted: #8b8fa3;
  --border-subtle: rgba(255, 255, 255, 0.08);
  --gradient-trust: linear-gradient(135deg, #00d4aa, #00b4d8);
  --gradient-danger: linear-gradient(135deg, #ff3b5c, #ff6b35);
}
```

**Typography:** Google Font — `Inter` (clean, modern, banking-appropriate)

### Step 2.2 — Login Page (index.html)

- Full-screen dark gradient background
- Centered glassmorphism login card
- Armadillo team logo at top
- "Project Sentinel" title with animated shield icon
- Username + password fields
- "Powered by Continuous Identity Trust" tagline
- On submit → call `/api/auth/login` → redirect to dashboard

### Step 2.3 — Banking Dashboard (dashboard.html)

**Layout:**

```
┌──────────────────────────────────────────────────┐
│  🛡️ Sentinel    Welcome, Priyansh    [Logout]    │ ← Header
├───────────┬──────────────────────────────────────┤
│           │                                      │
│   TRUST   │  💰 Account Balance                  │
│   SCORE   │  ₹4,52,380.00                        │
│           │                                      │
│   ●●●●●   │  Recent Transactions                 │
│    92     │  ├ -₹2,000  Swiggy        Today      │
│           │  ├ -₹15,000 Amazon        Yesterday  │
│  ┌─────┐  │  ├ +₹45,000 Salary       Jun 15      │
│  │Behav│  │  └ -₹500   Netflix       Jun 14      │
│  │67%  │  │                                      │
│  │Dev  │  │  Quick Actions                       │
│  │100% │  │  [Transfer] [Pay Bills] [Statements] │
│  │Sess │  │                                      │
│  │85%  │  │  ┌──────────────────────────────┐    │
│  │Graph│  │  │ Trust Score History (chart)    │  │
│  │100% │  │  └──────────────────────────────┘    │
│  └─────┘  │                                      │
└───────────┴──────────────────────────────────────┘
```

**Key Elements:**

- **Trust Score Gauge:** Large animated SVG circle (0-100), color-coded (green/yellow/red)
- **Sub-score breakdown:** 4 mini-bars showing Behavioral / Device / Session / Graph
- **Mock banking data:** Hardcoded account balance and transactions
- **Quick action buttons:** Transfer, Pay Bills, Statements (trigger different trust evaluations)

### Step 2.4 — The Silent Lock UI

When trust drops below 85 → the entire dashboard content gets:

```css
.dashboard-content.locked {
  filter: blur(20px) brightness(0.3);
  pointer-events: none;
  user-select: none;
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
```

And an MFA overlay slides up from the bottom:

```css
.mfa-overlay {
  backdrop-filter: blur(16px);
  background: var(--bg-glass);
  border-top: 1px solid var(--border-subtle);
  animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
```

---

## Phase 3: Telemetry SDK (JavaScript)

**⏱️ 1.5 hours | 1:30 - 3:00 AM**

### Step 3.1 — Keystroke Dynamics Collector (telemetry.js)

**What we capture per keystroke:**

```javascript
{
  key: "a",
  keyDownTime: 1718712345123,    // When key was pressed
  keyUpTime: 1718712345189,      // When key was released
  dwellTime: 66,                 // How long key was held (ms)
  flightTime: 123,               // Time since last key release (ms)
}
```

**Aggregate metrics sent every 3 seconds:**

```javascript
{
  avg_dwell_time: 78.3,          // Average ms key held
  avg_flight_time: 134.7,        // Average ms between keys
  std_dwell_time: 12.4,          // Consistency of dwell
  std_flight_time: 28.9,         // Consistency of flight
  typing_speed: 5.2,             // Characters per second
  sample_size: 47                // Keystrokes in this window
}
```

### Step 3.2 — Mouse Movement Tracker

**What we capture:**

```javascript
{
  avg_velocity: 342.5,           // px/sec average speed
  max_velocity: 1200.3,          // px/sec peak speed
  path_straightness: 0.73,       // 0=chaotic, 1=perfectly straight (bot-like)
  click_frequency: 0.8,          // Clicks per second
  direction_changes: 24,         // # of significant direction changes
  idle_time_ratio: 0.15          // % of time mouse was stationary
}
```

**Bot detection insight (from your research doc):**

> _"Automated banking trojans and click-farm scripts exhibit mathematically perfect, linear trajectories or rigid, inhuman timing patterns"_ — This is why `path_straightness > 0.95` is a strong fraud signal.

### Step 3.3 — Device Fingerprinting

Lightweight browser fingerprint (no library needed):

```javascript
{
  user_agent: "Mozilla/5.0...",
  screen_resolution: "1920x1080",
  timezone: "Asia/Kolkata",
  language: "en-US",
  color_depth: 24,
  platform: "Win32",
  hardware_concurrency: 8,       // CPU cores
  device_memory: 8,              // GB RAM
  canvas_hash: "a3f2b8c1...",    // Canvas rendering fingerprint
  webgl_renderer: "ANGLE...",    // GPU info
  touch_support: false           // Is touchscreen?
}
```

### Step 3.4 — API Integration

Every 3 seconds:

```
POST /api/telemetry/ingest
Authorization: Bearer <jwt>
Body: {
  session_id: "uuid",
  keystroke_metrics: { ... },
  mouse_metrics: { ... },
  device_fingerprint: { ... },  // Only sent once per session
  timestamp: 1718712345000
}

Response: {
  trust_score: 87,
  decision: "ALLOW",
  sub_scores: {
    behavioral: 78,
    device: 100,
    session: 85,
    graph: 100
  }
}
```

---

## Phase 4: Trust Score Engine (The Brain)

**⏱️ 1.5 hours | 3:00 - 4:30 AM**

### Step 4.1 — Behavioral Score (Weight: 40%)

**How it works — NO ML TRAINING NEEDED:**

1. **Enrollment phase (first 30 seconds of first login):**
   - Collect user's natural typing rhythm
   - Store average + standard deviation of dwell_time and flight_time
   - This becomes their "behavioral baseline"

2. **Continuous scoring (every 3 seconds after):**
   - Compare current typing metrics against stored baseline
   - Calculate z-score: `z = |current - baseline_avg| / baseline_std`
   - Higher z-score = bigger deviation = lower trust

```python
def compute_behavioral_score(current, baseline):
    score = 100.0

    # Flight time deviation (max -30 penalty)
    flight_z = abs(current.avg_flight - baseline.avg_flight) / max(baseline.std_flight, 1)
    score -= min(flight_z * 10, 30)

    # Dwell time deviation (max -25 penalty)
    dwell_z = abs(current.avg_dwell - baseline.avg_dwell) / max(baseline.std_dwell, 1)
    score -= min(dwell_z * 10, 25)

    # Typing speed deviation >30% (max -20 penalty)
    speed_ratio = current.typing_speed / max(baseline.avg_speed, 0.1)
    if speed_ratio > 1.3 or speed_ratio < 0.7:
        score -= 20

    # Mouse straightness check — bots move too perfectly
    if current.mouse_straightness > 0.95:
        score -= 15

    return max(score, 0)
```

> **🎯 Why this works for demo:** When YOU type → baseline matches → score ~90-100. When TEAMMATE types → different rhythm → score drops to ~50-65. Instant "wow" moment.

### Step 4.2 — Device Score (Weight: 20%)

```python
def compute_device_score(fingerprint, known_fingerprints):
    score = 0
    if fingerprint.hash in known_fingerprints:  score += 50  # Known device
    if fingerprint.timezone == "Asia/Kolkata":   score += 15  # Expected TZ
    if fingerprint.platform in user_platforms:   score += 20  # Known OS
    if fingerprint.screen in user_screens:       score += 15  # Known display
    return min(score, 100)
```

### Step 4.3 — Session Context Score (Weight: 20%)

```python
def compute_session_score(session):
    score = 100
    hour = datetime.now().hour
    if not (8 <= hour <= 22):  score -= 25     # Unusual hours
    if session.requests_per_min > 30: score -= 30  # Burst = bot
    if session.duration_min > 60: score -= 15      # Unusually long
    return max(score, 0)
```

### Step 4.4 — Graph Risk Score (Weight: 20%)

```python
def compute_graph_score(user_id, neo4j_driver):
    # Check: Does this user's device/IP overlap with flagged accounts?
    query = """
    MATCH (u:User {id: $uid})-[:USES_DEVICE]->(d:Device)
          <-[:USES_DEVICE]-(other:User {flagged: true})
    RETURN count(other) as shared
    """
    result = neo4j_driver.run(query, uid=user_id)
    if result.shared > 0: return 20   # Shares device with fraud
    return 100  # Clean
```

### Step 4.5 — Composite Score + Decision

```python
COMPOSITE = (0.40 × Behavioral) + (0.20 × Device) + (0.20 × Session) + (0.20 × Graph)

if COMPOSITE > 85  → "ALLOW"      ✅ Zero friction
if COMPOSITE 55-85 → "STEP_UP"    ⚠️ Trigger MFA challenge
if COMPOSITE < 55  → "BLOCK"      🚫 Lock + alert SecOps
```

---

## Phase 5: Adaptive MFA Flow

**⏱️ 1.5 hours | 4:30 - 6:00 AM**

### Step 5.1 — MFA Method Selection (The "Adaptive" Part)

This is what makes Sentinel special — the MFA type changes based on WHY trust dropped:

```python
def select_mfa_method(trust_context):
    if trust_context.behavioral_anomaly:
        return "FACE_LIVENESS"    # Different person typing → OTP useless, need biometric
    if trust_context.device_changed:
        return "TOTP"             # New device → authenticator app code
    if trust_context.geo_anomaly:
        return "TOTP"             # Remote access → standard re-auth
    if trust_context.admin_sop_violation:
        return "MANAGER_APPROVAL" # Insider threat → human review
    return "TOTP"                 # Default fallback
```

**Why this matters (from your research):**

> _"If a device is snatched while unlocked, a text-based OTP is useless — the thief has the phone."_ So Sentinel forces facial liveness instead, because the thief cannot replicate the legitimate user's face.

### Step 5.2 — TOTP (Google Authenticator)

**Registration flow:**

1. Backend generates secret: `pyotp.random_base32()`
2. Creates QR code: `pyotp.totp.TOTP(secret).provisioning_uri("user@bob.com", "Sentinel")`
3. User scans QR with Google Authenticator
4. Secret stored in `users.totp_secret`

**Verification flow:**

1. User enters 6-digit code from authenticator
2. Backend verifies: `pyotp.TOTP(secret).verify(code, valid_window=1)`
3. If valid → trust score recovers to 90, session continues
4. If invalid → attempt counter++, block after 3 fails

### Step 5.3 — Face Liveness Challenge (Simulated)

**What we build for prototype:**

1. When triggered, show webcam modal with instruction: _"Look at the camera, then slowly turn your head left"_
2. Use `navigator.mediaDevices.getUserMedia({ video: true })` to activate front camera
3. Capture 3 frames at 1-second intervals
4. **For prototype:** Simulate verification with a 3-second "analyzing..." animation → pass
5. **For judges:** Explain this would use FaceTec SDK or AWS Rekognition in production

**The UX is the demo — not the ML behind it.**

### Step 5.4 — MFA Challenge UI

```
┌─────────────────────────────────────────┐
│  🔒 Identity Verification Required       │
│                                          │
│  ⚠️ Unusual typing pattern detected      │
│  Your behavioral signature doesn't match │
│  the account owner's profile.            │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │  📷 Facial Liveness Check         │    │
│  │                                    │    │
│  │  [Webcam feed here]               │    │
│  │                                    │    │
│  │  Please look at the camera and    │    │
│  │  slowly turn your head LEFT       │    │
│  └──────────────────────────────────┘    │
│                                          │
│  ── OR ──                                │
│                                          │
│  Enter TOTP code: [_ _ _ _ _ _]          │
│                                          │
│  [Verify Identity]                       │
│                                          │
│  Trust Score: 62 ⚠️                      │
└─────────────────────────────────────────┘
```

---

## Phase 6: Neo4j Fraud Ring Graph

**⏱️ 1.5 hours | 6:00 - 7:30 AM**

### Step 6.1 — Create the Fraud Graph Schema

Run these Cypher queries in your Neo4j Aura console (or via the seed script):

```cypher
// Constraints
CREATE CONSTRAINT FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT FOR (d:Device) REQUIRE d.imei IS UNIQUE;
CREATE CONSTRAINT FOR (ip:IP) REQUIRE ip.address IS UNIQUE;
CREATE CONSTRAINT FOR (a:Account) REQUIRE a.number IS UNIQUE;
```

### Step 6.2 — Seed 3 Fraud Scenarios

**Ring 1: "The Mule Network" — 12 connected mule accounts**

```cypher
// 2 shared devices used by 12 "different" users
CREATE (d1:Device {imei: "353456789012345", model: "Redmi Note 12", os: "Android 14", flagged: true})
CREATE (d2:Device {imei: "353456789012346", model: "Samsung A54", os: "Android 13", flagged: true})

// Shared VPN IPs
CREATE (ip1:IP {address: "103.21.45.67", is_vpn: true, geo: "Lagos, Nigeria"})
CREATE (ip2:IP {address: "103.21.45.68", is_vpn: true, geo: "Lagos, Nigeria"})

// 12 fake users, all using the same 2 devices
FOREACH (i IN range(1,6) |
  CREATE (u:User {id: 100+i, name: "User_"+i, account: "BOB"+i, flagged: true, risk: "HIGH"})
  CREATE (u)-[:USES_DEVICE]->(d1)
  CREATE (u)-[:CONNECTS_FROM]->(ip1)
)
FOREACH (i IN range(7,12) |
  CREATE (u:User {id: 100+i, name: "User_"+i, account: "BOB"+i, flagged: true, risk: "HIGH"})
  CREATE (u)-[:USES_DEVICE]->(d2)
  CREATE (u)-[:CONNECTS_FROM]->(ip2)
)

// Central mule hub receiving all transfers
CREATE (hub:Account {number: "BOB_HUB_001", type: "Current", bank: "BOB", is_mule: true})
```

**Ring 2: "The Insider" — Banker accessing accounts at 2 AM**

```cypher
CREATE (banker:User {id: 200, name: "Rajesh_Teller", role: "BANKER", branch: "Ahmedabad_Main", flagged: true, risk: "CRITICAL"})
CREATE (hnw1:User {id: 201, name: "HNW_Client_A", account: "BOB_HNW_001", net_worth: "₹2.3Cr"})
CREATE (hnw2:User {id: 202, name: "HNW_Client_B", account: "BOB_HNW_002", net_worth: "₹5.1Cr"})
CREATE (banker)-[:ACCESSED_RECORD {time: "02:15 AM", ticket: "NONE"}]->(hnw1)
CREATE (banker)-[:ACCESSED_RECORD {time: "02:32 AM", ticket: "NONE"}]->(hnw2)
CREATE (banker)-[:BULK_EXPORT {records: 847, time: "02:45 AM"}]->(hnw1)
```

**Ring 3: "Clean Users" — Normal behavior (for contrast)**

```cypher
FOREACH (i IN range(1,8) |
  CREATE (u:User {id: 300+i, name: "Clean_User_"+i, flagged: false, risk: "LOW"})
  CREATE (d:Device {imei: "CLEAN_IMEI_"+i, model: "iPhone 15"})
  CREATE (ip:IP {address: "49.36."+i+"."+i, is_vpn: false, geo: "Mumbai"})
  CREATE (u)-[:USES_DEVICE]->(d)
  CREATE (u)-[:CONNECTS_FROM]->(ip)
)
```

### Step 6.3 — Graph Visualization (Neovis.js)

Embed an interactive graph on the SOC dashboard using **Neovis.js** (free library):

```html
<script src="https://unpkg.com/neovis.js@2.0.2"></script>
<div id="fraud-graph" style="width: 100%; height: 500px;"></div>
```

Configuration:

- **Red nodes** = Flagged users
- **Green nodes** = Clean users
- **Orange edges** = Shared device connections
- **Purple nodes** = Devices
- **Gray nodes** = IP addresses
- Clusters automatically form visible "rings"

---

## Phase 7: SOC Dashboard

**⏱️ 1 hour | 7:30 - 8:30 AM**

### Step 7.1 — SOC Dashboard Layout (soc.html)

```
┌──────────────────────────────────────────────────────┐
│  🛡️ Sentinel SOC │ Active Sessions: 3 │ Alerts: 5   │
├──────────────────┬───────────────────────────────────┤
│  ALERTS FEED     │  FRAUD RING GRAPH                 │
│  ─────────────── │                                   │
│  🔴 CRITICAL     │  ┌───────────────────────────┐    │
│  ATO Detected    │  │                           │    │
│  User: priyansh  │  │   [Interactive Neo4j      │    │
│  2 min ago       │  │    Graph Visualization]   │    │
│  ─────────────── │  │                           │    │
│  🟡 WARNING      │  │   12 connected mule       │    │
│  Unusual typing  │  │   accounts detected       │    │
│  User: demo      │  │                           │    │
│  5 min ago       │  └───────────────────────────┘    │
│  ─────────────── │                                   │
│  🟢 INFO         │  TRUST SCORE HISTORY              │
│  New device      │  ┌───────────────────────────┐    │
│  User: admin     │  │ [Line chart showing score │    │
│  12 min ago      │  │  drops and recoveries]    │    │
│                  │  └───────────────────────────┘    │
├──────────────────┴───────────────────────────────────┤
│  ACTIVE SESSIONS MONITOR                             │
│  ┌─────────────────────────────────────────────────┐ │
│  │ User     │ Trust │ Device    │ IP        │ Time │ │
│  │ priyansh │  92   │ Chrome/W  │ 49.36.x.x│ 5m   │ │
│  │ demo     │  67 ⚠ │ Firefox   │ 103.x.x.x│ 12m  │ │
│  │ admin    │  45 🚫│ Unknown   │ TOR exit  │ 1m   │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

---

## Phase 8: Polish + Demo Prep

**⏱️ 1.5 hours | 8:30 - 10:00 AM**

### Step 8.1 — Demo Data Seeder Script

Create `seed_demo.py` that:

1. Creates 3 user accounts: `priyansh` (you), `demo` (legitimate), `attacker` (for testing)
2. Pre-populates behavioral baselines for `priyansh` (so trust starts high)
3. Seeds Neo4j with all 3 fraud rings
4. Creates sample trust logs and alerts

### Step 8.2 — UI Polish Checklist

- [ ] Trust gauge animation smooth (CSS transitions on SVG)
- [ ] Blur transition feels natural (800ms cubic-bezier)
- [ ] MFA overlay slides up elegantly (600ms ease-out)
- [ ] SOC alerts auto-refresh every 5 seconds
- [ ] Loading spinners on all API calls
- [ ] Error toasts for failed requests
- [ ] Armadillo logo in header
- [ ] "Project Sentinel" branding consistent everywhere
- [ ] Responsive on laptop screen (1366px+)

### Step 8.3 — Demo Rehearsal Script

**Act 1: "The Trusted User" (2 minutes)**

1. Open `http://localhost:8000` → Sentinel login page
2. Login as `priyansh` → Dashboard loads, trust score = **92** ✅
3. Click around, type in search, initiate mock transfer
4. Trust stays high → Zero friction
5. SAY: _"I've been using this app naturally. No OTP, no interruption. The system trusts me based on how I type and interact."_

**Act 2: "The Account Takeover" (2 minutes)**

1. Hand laptop to teammate (the "attacker")
2. They start typing and navigating → Trust score drops live: 92 → 78 → **63** ⚠️
3. Screen blurs beautifully → MFA overlay appears
4. Message: _"Unusual typing pattern detected. Verify your identity."_
5. System chose **Face Liveness** (not OTP — because the attacker has the device)
6. Attacker cannot pass face check → **BLOCKED** 🚫
7. SAY: _"The system detected a different human typing. Not a password breach — a behavioral breach."_

**Act 3: "The Fraud Network" (1 minute)**

1. Switch to SOC dashboard
2. Show live alert: "ATO Detected — User: priyansh"
3. Click Neo4j graph → Show 12 interconnected mule accounts
4. SAY: _"Graph Memory catches fraud rings that per-account analysis misses. These 12 accounts share 2 devices and a VPN IP range."_

**Closing (30 seconds)**

- _"Sentinel saves BoB crores in SMS OTP costs annually"_
- _"DPDP Act compliant — raw biometrics never leave the browser"_
- _"Works across web, mobile, and admin channels"_
- _"Behavioral biometrics + graph memory + adaptive MFA = next-gen banking security"_

---

## Run Command (Single Command to Start)

```powershell
cd "d:\Hackathon\PSB Hackathon IIT Gandhinagar\sentinel-prototype"
.\venv\Scripts\activate
python run.py
```

This starts:

- FastAPI server on `http://localhost:8000`
- Serves frontend automatically
- Connects to Neo4j Aura
- Ready for demo

---

## Risk Mitigation

| Risk                                  | Mitigation                                           |
| ------------------------------------- | ---------------------------------------------------- |
| Neo4j Aura is slow/down               | Have pre-recorded screenshots of the graph as backup |
| Webcam doesn't work on jury laptop    | Have TOTP as fallback MFA (always works)             |
| Trust score doesn't drop dramatically | Pre-set a "demo mode" with exaggerated sensitivity   |
| WiFi issues during presentation       | Run 100% locally, Neo4j data cached                  |
| Teammate not available for Act 2      | Ask a jury member to type — even more impressive     |

---

> **⚡ START NOW. Phase 0 first — create the Neo4j account while I build the code.**
