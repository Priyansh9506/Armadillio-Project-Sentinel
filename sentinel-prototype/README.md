# 🛡️ Project Sentinel (Team Armadillo)

**Next-Generation Continuous Authentication & Fraud Prevention for Banking**

Project Sentinel is a prototype designed to replace traditional, static authentication (like single-use passwords) with a dynamic, continuous trust-scoring system. It seamlessly protects users against session hijacking, coercion, and identity fraud using real-time behavioral biometrics, adaptive MFA, and silent duress alarms.

## ✨ Key Features

1. **Continuous Trust Gauge (Behavioral Biometrics)**
   - Monitors user behavior (typing speed, cursor movements) in the background.
   - Dynamically calculates a **Trust Score (0-100)**.
   - If trust drops, the system adaptively steps up authentication.

2. **Adaptive MFA (Push Auth Challenge)**
   - Triggered automatically for sensitive actions (like changing UPI PINs) or when the Trust Score drops.
   - Uses a secure **3-Number Matching** Push Auth challenge, simulating a trusted mobile device verification.

3. **Duress PIN & Silent Alarms**
   - Users can append a secret suffix (e.g., `9999`) to their UPI/Transaction PIN during a robbery or coercion scenario.
   - The UI fakes a successful transaction, but the backend secretly holds the funds and flags a **CRITICAL** alert on the SOC dashboard.

4. **Real-time SOC (Security Operations Center) Dashboard**
   - A live dashboard for bank security teams to monitor active sessions, fraud rings (Graph analysis), and incoming alerts.
   - Dual-writes to both local SQLite (for fast local prototyping) and **Supabase (PostgreSQL)** for cloud-scale telemetry logging.

## 🛠️ Tech Stack

- **Frontend**: React (Vite), Vanilla CSS (Custom modern UI/UX design)
- **Backend**: Python (FastAPI), Uvicorn
- **Database**: SQLite (Local SOC caching) & Supabase / PostgreSQL (Cloud transactions)
- **Authentication**: JWT & PyOTP (TOTP)
- **Encryption**: Bcrypt for PIN hashing

## 🚀 How to Run Locally

### 1. Backend Setup (FastAPI)
Open a terminal in the `backend` directory:
```bash
cd backend
# Create and activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the database migration (if starting fresh)
python migrate.py
python seed_data.py

# Start the server
uvicorn main:app --reload
```
*The backend will run at `http://localhost:8000`.*

### 2. Frontend Setup (React)
Open a new terminal in the `frontend` directory:
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
*The frontend will run at `http://localhost:5173`.*

## 🌩️ Cloud Integration (Supabase)
To enable real-time cloud database logging:
1. Copy `backend/.env.example` to `backend/.env`.
2. Add your `SUPABASE_URL` and `SUPABASE_KEY`.
3. The backend `supabase_client.py` will automatically detect the keys and begin dual-writing transactions.

## 💡 Hackathon Demo Instructions
1. **Login**: Use username `priyansh` and password `password`.
2. **Behavioral Drop**: Type erratically or click rapidly to drop the Trust Score.
3. **MFA Challenge**: Click **Change PIN** in the dashboard. Click the pulsing number on the screen to simulate a trusted device and instantly change your PIN.
4. **Duress Demo**: Make a UPI payment using PIN `12349999`. The UI shows success, but check the **SOC Dashboard** to see the intercepted transaction!

---
*Built with ❤️ by Team Armadillo for the PSB Hackathon at IIT Gandhinagar.*
