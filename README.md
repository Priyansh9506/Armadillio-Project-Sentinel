<div align="center">
  <h1>🛡️ Project Sentinel</h1>
  <p><b>Continuous Identity Trust & Behavioral Biometrics Platform</b></p>
  
  [![React](https://img.shields.io/badge/React-18.x-blue.svg)](https://reactjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
  [![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/)
  [![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E.svg)](https://supabase.com/)
</div>

---

## 📖 Overview

**Project Sentinel** is an enterprise-grade identity security platform that replaces static "verify-once" paradigms with **Continuous Authentication**. By silently monitoring behavioral biometrics (keystroke dynamics, mouse pathing, device telemetry), Sentinel establishes a baseline and generates a real-time **Trust Score** for every user session.

This repository contains the complete prototype built for the **PSB Hackathon @ IIT Gandhinagar**. It includes a simulated banking frontend, a high-throughput telemetry API, a machine-learning scoring engine mock, and a Security Operations Center (SOC) dashboard.

---

## 🏗️ System Architecture

Project Sentinel utilizes a decoupled architecture prioritizing high-throughput telemetry ingestion without blocking core banking transactions.

### Prototype Architecture
![Prototype Architecture](./Archirtecture/Project%20Sentinel%20Architecture-Prototype-v2.png)

### Full Enterprise Architecture
![Enterprise Architecture](./Archirtecture/Project%20Sentinel%20Architecture-Enterprise%20Architecture.png)

### Technical Design Decisions

1. **Dual-Database Approach:**
   - **SQLite:** Acts as a high-speed, edge-like data store for telemetry events and the SOC dashboard. Telemetry pinging every 3 seconds requires massive write throughput.
   - **Supabase (PostgreSQL):** Acts as the single source of truth for persistent states like user accounts, password hashes, and finalized transaction ledgers.
2. **Behavioral Telemetry SDK:** A custom lightweight JS SDK tracks `keydown`, `keyup`, and `mousemove` events. It locally computes derivatives (velocity, dwell time, flight time) and batches them to reduce network overhead.
3. **Cryptography:** Uses **Bcrypt with Salt + System Pepper** for storing sensitive PINs and passwords, protecting against rainbow table and database exfiltration attacks.

---

## 📂 Directory Structure

```text
sentinel-prototype/
├── backend/
│   ├── auth/                # JWT Auth routes, Login, Password changes
│   ├── mfa/                 # Push Auth & Voice Liveness simulations
│   ├── payments/            # Core banking APIs, NEFT, UPI, Bills
│   ├── soc/                 # Endpoints feeding the Analyst Dashboard
│   ├── telemetry/           # High-throughput ingestion API
│   ├── database.py          # SQLite schema & connection pooling
│   ├── supabase_client.py   # Cloud sync handlers
│   └── main.py              # FastAPI application entry point
│
└── frontend/
    ├── src/
    │   ├── api.js           # Axios instance & JWT Interceptors
    │   ├── components/      # Reusable UI (TrustGauge, MFAChallenge)
    │   ├── pages/           # Dashboard, SOC, Login, Register
    │   └── sdk/             # Behavioral Telemetry JS Client
    └── package.json
```

---

## 🚀 Core Features & Implementation Details

### 1. Continuous Behavioral Authentication
The `Telemetry SDK` analyzes:
- **Flight Time:** Delay between releasing one key and pressing the next.
- **Dwell Time:** Duration a key is held down.
- **Cursor Pathing:** Analysis of human micro-jitters vs. programmatic straight-line bot movements.

### 2. Context-Aware Step-Up MFA
If the `Risk Scoring Engine` drops a user's trust score below `80%` (e.g., erratic typing), the API rejects critical endpoints (`/payments/upi/send`) with a `403 Step-Up Required` status. The frontend intercepts this and forces a friction-right Push Auth or Voice Liveness check.

### 3. Duress Mode (Silent Alarm Mechanism)
A patented conceptual workflow to protect victims of physical coercion.
- A user sets a primary PIN (e.g., `1234`).
- A system-wide duress suffix is defined (e.g., `9999`).
- If `12349999` is entered, `verify_pin()` validates it, executes the transaction locally as `STATUS_SUCCESS` (to satisfy the attacker), but internally flags it as `DURESS_HELD` in the database, firing a WebSocket/Polling alert to the SOC dashboard.

---

## 💻 Developer Setup

### Prerequisites
- Node.js (v18+)
- Python (3.10+)

### 1. Backend Setup

```bash
cd sentinel-prototype/backend

# Create virtual environment
python -m venv venv

# Activate environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed the Local SQLite & Cloud database (Crucial for Demo)
python seed_data.py

# Start the development server
uvicorn main:app --reload --port 8000
```
*The FastAPI Swagger UI will be available at [http://localhost:8000/docs](http://localhost:8000/docs).*

### 2. Frontend Setup

```bash
cd sentinel-prototype/frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
*The React App will be available at [http://localhost:5173](http://localhost:5173).*

---

## 🧪 Documentation & Testing

- **API Documentation:** Auto-generated by FastAPI at `/docs`.
- **Demo Scripts:** Check `demoscript.md` for a step-by-step walkthrough of the platform's capabilities designed for hackathon judges.
- **Credentials:** Refer to `credentials.md` for default seed accounts.

---
**License:** MIT  
**Authors:** Team Armadillo
