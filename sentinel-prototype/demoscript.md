# 🎬 Sentinel Hackathon Demo Script

Follow this script step-by-step to showcase the core features of Project Sentinel to the judges.

## Preparation
- Ensure both the React frontend (`npm run dev`) and FastAPI backend (`uvicorn main:app`) are running.
- Keep the `credentials.md` file handy.

---

## Step 1: The Login & Baseline Trust (The "Good" State)
1. Navigate to `http://localhost:5173`.
2. Login as **Vyom**:
   - **Mobile:** `9123456789`
   - **Password:** `password123`
3. **Talk Track:** *"This is the Bank of Baroda dashboard secured by Armadillo's Sentinel AI. Notice the Trust Gauge on the left is green (100%). Sentinel has recognized Vyom's device and behavior, granting him full frictionless access."*
4. Click **Transfer**, enter `1234` for the PIN, and transfer ₹500. It succeeds instantly without extra checks.

## Step 2: The Anomaly & Continuous Auth (Account Takeover)
1. **Talk Track:** *"Now, imagine a fraudster stole Vyom's laptop while it was unlocked. They don't type like Vyom, and their mouse movements are erratic."*
2. Click the **Demo: Auto-Lock ON** button (bottom right of the banking card). This simulates a drastic drop in the behavioral Trust Score.
3. The screen will instantly lock with a **"Security Lock Activated"** warning.
4. **Talk Track:** *"Sentinel detected the anomaly in real-time and dynamically introduced friction. The fraudster is locked out. Let's verify our identity to regain access."*
5. Click **Verify via Push Auth** and complete the mock MFA challenge to restore the Trust Score to green. Turn the Demo Auto-Lock OFF.

## Step 3: Changing the PIN (High-Risk Action)
1. Click **Change PIN**.
2. Explain that changing a PIN is a high-risk action.
3. Enter Old PIN (`1234`) and New PIN (`5678`). 
4. The system forces a Push Auth MFA challenge before allowing the PIN change. Complete it.
5. The PIN is now successfully changed.

## Step 4: The Duress Scenario (Silent Alarm)
1. **Talk Track:** *"Let's look at a physical coercion scenario. Someone has a knife to Vyom and forces him to transfer ₹50,000 to their mule account."*
2. Click **Transfer**.
3. Enter Receiver Account: `999999999` and Amount: `50000`.
4. Enter the **Duress PIN**. This is the new PIN (`5678`) plus the secret duress suffix (`9999`). So, enter: `56789999`.
5. Click **Confirm Transfer**.
6. **Talk Track:** *"The UI shows a green checkmark! The attacker thinks they got the money and leaves. But let's look at what actually happened behind the scenes."*

## Step 5: The SOC Dashboard & Fraud Ring Graph
1. Click the **SOC Dashboard** button at the top right.
2. **Talk Track:** *"This is the Security Operations Center for the bank."*
3. Point to the **Recent Alerts** table. Show the critical red alert: **"DURESS ALERT: Silent alarm triggered during transfer... Funds routed to holding account."**
4. Explain that the money was never actually sent to the attacker.
5. Scroll down to the **Fraud Ring Detection Graph**. Show how Sentinel maps shared devices and suspicious IPs to visualize organized crime rings.

## Conclusion
*"Sentinel replaces static passwords with dynamic, invisible security that protects users from digital account takeovers and physical coercion, without adding unnecessary friction to their daily banking."*
