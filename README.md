<div align="center">
  <img src="Armadillo-Logo.png" alt="Armadillo Logo" width="150"/>

  # 🛡️ Project Sentinel
  **Next-Generation Continuous Authentication & Fraud Prevention**
  
  *Built by Team Armadillo for the PSB Hackathon 2026 @ IIT Gandhinagar*

  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
  [![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
  [![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
  [![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)](https://vitejs.dev/)

</div>

---

> Traditional banking relies on static, single-use authentication (passwords, OTPs). Once a bad actor crosses the gate, they have complete control. **Project Sentinel changes the game.** We assume compromise and verify continuously. 

Project Sentinel is a fully-functional banking security prototype that replaces static login walls with a **Dynamic Trust-Scoring Engine**. By utilizing real-time behavioral biometrics, adaptive Multi-Factor Authentication (MFA), and silent duress mechanisms, Sentinel protects users against session hijacking, coercion (gunpoint robberies), and sophisticated identity fraud.

---

## ⚡ Killer Features

### 1. 🧬 Continuous Trust Engine (Behavioral Biometrics)
Sentinel doesn't just authenticate you when you log in; it authenticates you *while* you use the app.
- Monitors typing cadence, cursor erraticism, and session telemetry invisibly in the background.
- Dynamically calculates a **Trust Score (0-100)**.
- If a session is hijacked and the Trust Score plunges, Sentinel adaptively enforces step-up authentication.

### 2. 🔐 Adaptive Push Auth MFA
Phishing-resistant, frictionless security for high-risk actions.
- Triggered automatically when modifying sensitive data (like changing UPI PINs) or during low-trust scenarios.
- Features a secure **3-Number Matching Challenge**, simulating a hardware-bound trusted mobile device verification to prevent man-in-the-middle (MITM) attacks.

### 3. 🚨 The "Duress Suffix" & Silent Alarms
What happens if a user is forced to transfer money at knifepoint?
- Users can append a secret "Duress Suffix" (e.g., `9999`) to their actual UPI/Transaction PIN.
- **The Magic:** The UI displays a "Payment Successful" screen to fool the attacker, but the backend secretly intercepts the funds, freezes the transfer, and flags a **CRITICAL** silent alarm to the bank.

### 4. 👁️‍🗨️ Real-Time SOC (Security Operations Center)
A God's-eye view for bank security teams.
- Live dashboard tracking active sessions, real-time trust gauges, and immediate alerts for duress scenarios.
- Advanced graph-ready telemetry logging, dual-written to local SQLite (for extreme speed) and **Supabase (PostgreSQL)** (for cloud-scale analytics).

---

## 🛠️ Architecture & Tech Stack

<details>
<summary><b>Click to expand Tech Stack details</b></summary>

- **Frontend Environment**: React 18 powered by Vite.
- **Styling**: Vanilla CSS (Tailored glassmorphism, fluid animations, and custom design tokens for a premium banking feel).
- **Backend Framework**: Python FastAPI running on Uvicorn for asynchronous, high-throughput requests.
- **Database Strategy**: 
  - *Local Tier*: SQLite (Handles rapid telemetry caching and local SOC data).
  - *Cloud Tier*: Supabase / PostgreSQL (Handles persistent transaction ledgers and cross-device sync).
- **Security & Auth**: JWT for stateless session management, PyOTP for TOTP generation, and Bcrypt for aggressive PIN hashing.

</details>

---

## 🚀 Get Started (Local Deployment)

Want to run the magic yourself? Follow these steps.

### 🐍 1. Backend Setup (FastAPI)

Fire up a terminal and dive into the backend:

```bash
cd sentinel-prototype/backend

# Create and activate a virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install the heavy lifting dependencies
pip install -r requirements.txt

# Initialize the database and inject seed data
python migrate.py
python seed_data.py

# Ignite the server! 🔥
uvicorn main:app --reload
```
*The backend API will be live at `http://localhost:8000`.*

### ⚛️ 2. Frontend Setup (React/Vite)

Open a new terminal and prepare the UI:

```bash
cd sentinel-prototype/frontend

# Install node modules
npm install

# Start the lightning-fast dev server
npm run dev
```
*The banking app will be live at `http://localhost:5173`.*

---

## 🌩️ Cloud Mode (Supabase Integration)

To unlock real-time cloud database logging across devices:
1. Copy `backend/.env.example` to `backend/.env`.
2. Inject your `SUPABASE_URL` and `SUPABASE_KEY`.
3. The backend `supabase_client.py` will auto-detect the keys and magically begin dual-writing all critical transactions to the cloud.

---

## 🎮 The Hackathon Demo Script

Impress the judges by following this exact sequence:

1. **The Entry:** Login using username `priyansh` and password `password`.
2. **The Hijack (Behavioral Drop):** Start typing erratically, mash the keyboard, or move the mouse wildly to watch the Trust Score plummet in real-time.
3. **The Step-Up (MFA Challenge):** Navigate to the dashboard and click **Change PIN**. The system demands proof of life. Click the pulsing verification number on the screen to simulate a trusted secondary device and securely change the PIN.
4. **The Robbery (Duress Demo):** Initiate a UPI payment. When asked for the PIN, type `12349999` (Base PIN + Duress Suffix). 
5. **The Reveal:** Watch the UI show a fake "Success" screen. Then, switch to the **SOC Dashboard** to reveal the intercepted transaction and the blaring silent alarm!

---

<div align="center">
  <b>Built for the future of banking. Built by Team Armadillo. 🚀</b>
</div>
