# 🛡️ Project Sentinel by Team Armadillo

**Identity Trust & Continuous Authentication Platform**  
Built for the **PSB Hackathon @ IIT Gandhinagar** (Bank of Baroda Problem Statement)

Project Sentinel is a next-generation security platform that abandons the traditional "verify once" login model. Instead, it continuously monitors behavioral biometrics, device intelligence, and transaction graphs to assign a real-time **Trust Score** to the user. If the trust score drops due to anomalous behavior, it automatically triggers friction-right Step-Up Authentication (e.g., Push Auth, Voice Liveness) to re-verify the user without breaking their flow.

---

## ✨ Key Features

### 1. Continuous Authentication (Invisible Security)
- **Keystroke Dynamics:** Analyzes flight time and dwell time.
- **Mouse Movement Analysis:** Tracks mouse velocity and path straightness to detect bots.
- **Silent Telemetry:** Sends behavioral data to the backend every 3 seconds without interrupting the user.

### 2. Multi-Dimensional Trust Engine
The ML-driven trust engine computes a composite score (0-100) based on:
- **Behavioral Score (30%):** Keystrokes and mouse patterns vs. seeded baseline.
- **Device Score (20%):** Browser fingerprinting, canvas hashing, resolution, and timezone checks.
- **Session Context (15%):** Time of day (IST), request frequency, and IP reputation.
- **Transaction Score (15%):** Anomaly detection based on the user's past transfer limits.
- **Graph Score (20%):** Real-time queries to Neo4j to see if the recipient is connected to a known fraud ring.

### 3. Adaptive Step-Up MFA
When the Trust Score drops below the safety threshold, the system triggers dynamic challenges:
- **Push Authentication:** Sends a "Select Number X" challenge to the user's trusted mobile device via WebSockets.
- **Voice Liveness (Mocked):** Prompts the user to read a specific generated phrase.

### 4. Security Operations Center (SOC)
- **Live Threat Monitoring:** Real-time dashboard showing active sessions, live trust scores, and connected IPs.
- **Alert Feed:** Automatically logs CRITICAL and HIGH severity events (e.g., Account Takeover Suspected, Insider Threat, Fraud Ring Activity).
- **Global Map & Telemetry:** Visualizes where attacks are originating from.

---

## 🛠️ Tech Stack

**Frontend:**
- **Framework:** React.js + Vite
- **Styling:** Custom Vanilla CSS with Glassmorphism UI
- **Data Visualization:** Recharts (for SOC Dashboard)

**Backend:**
- **Framework:** FastAPI (Python 3)
- **Database:** SQLite (Users, Sessions, Trust Logs, Challenges)
- **Graph Database:** Neo4j (Fraud Ring Analysis & Money Muling tracking)
- **Real-Time Comm:** WebSockets (for instant Push Auth notifications)

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.9+)
- Neo4j AuraDB (or local Neo4j instance)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file and add your Neo4j credentials
echo "NEO4J_URI=neo4j+s://<your-db>.databases.neo4j.io" > .env
echo "NEO4J_USER=neo4j" >> .env
echo "NEO4J_PASSWORD=<password>" >> .env

# Seed the database (Creates test users and mock fraud ring graph)
python seed_data.py

# Run the backend
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Accessing the App
- **Customer Dashboard:** `http://localhost:5173/login`
- **SOC Dashboard:** `http://localhost:5173/soc`

---

## 🎭 Demo Guide (For Hackathon Presenters)

To ensure a smooth presentation, the frontend includes a **Demo Control Toggle** on the customer dashboard.
1. Log in using the test credentials (e.g., `9876543210` / `password123`).
2. By default, **Auto-Lock is OFF**. You can freely show the UI, transfer money, and explore without being interrupted.
3. To demonstrate the Continuous Auth feature, click the **Demo: Auto-Lock OFF** button to turn it **ON**.
4. Perform an anomalous action (like typing erratically or triggering a high-value transfer to a suspicious account). The system will instantly lock the screen and demand Push Authentication.

## 👥 Team Armadillo
- Built with ❤️ during the PSB Hackathon @ IIT Gandhinagar.
