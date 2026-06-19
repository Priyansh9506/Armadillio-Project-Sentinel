# 🏗️ Project Sentinel — Roadmap 2: Full 1-Month Development
## June 20 → July 26, 2026 (Prototype Submission Deadline)
## Team Armadillo

---

## Timeline Overview (5 Weeks)

```
Week 0 (Jun 20-22)  ── Post-Idea Submission Stabilization
Week 1 (Jun 23-29)  ── Core Architecture & Real ML Pipeline
Week 2 (Jun 30-Jul 6) ── Advanced Features & Graph Intelligence
Week 3 (Jul 7-13)   ── Mobile + FIDO2/Passkeys + Insider Threat
Week 4 (Jul 14-20)  ── Integration Testing, Security Hardening, DPDP Compliance
Week 5 (Jul 21-26)  ── Final Polish, Demo Video, Deployment, Submission
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FULL ARCHITECTURE TARGET                         │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Web App  │  │ Mobile   │  │ Admin Portal │  │  SOC Console │   │
│  │ (React)  │  │ (Flutter)│  │ (React)      │  │  (React)     │   │
│  └────┬─────┘  └────┬─────┘  └──────┬───────┘  └──────┬───────┘   │
│       └──────────────┴───────────────┴─────────────────┘           │
│                              │                                      │
│                    ┌─────────┴──────────┐                          │
│                    │   API Gateway      │                          │
│                    │   (FastAPI + Go)   │                          │
│                    └─────────┬──────────┘                          │
│                              │                                      │
│  ┌───────────┬───────────┬───┴───┬────────────┬─────────────────┐  │
│  │ Auth &    │ Telemetry │ Trust │ MFA        │ Graph           │  │
│  │ Passkeys  │ Ingest    │ Score │ Engine     │ Intelligence    │  │
│  │ Service   │ Service   │Engine │ (Adaptive) │ (Neo4j)         │  │
│  └─────┬─────┴─────┬─────┴───┬───┴─────┬──────┴────────┬────────┘  │
│        │           │         │         │              │            │
│  ┌─────┴───┐ ┌─────┴────┐ ┌─┴────┐ ┌──┴──────┐ ┌────┴──────┐   │
│  │PostgreSQL│ │ Redis    │ │ ML   │ │ TOTP/   │ │ Neo4j     │   │
│  │ + FIDO2  │ │ Streams  │ │Models│ │ FIDO2   │ │ Aura Pro  │   │
│  └─────────┘ └──────────┘ │ Store│ │ FaceTec │ └───────────┘   │
│                            └──────┘ └─────────┘                   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Infrastructure: Docker Compose → Kubernetes (optional)       │   │
│  │ CI/CD: GitHub Actions │ Monitoring: Prometheus + Grafana     │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Full Production Tech Stack

| Layer | Prototype (Week 0) | Production (Week 5) | Why Upgrade |
|---|---|---|---|
| **Frontend Web** | React 18 + Vite | React 18 + Vite (Micro-frontends) | Scale to enterprise |
| **Frontend Mobile** | None | Flutter 3.x | Cross-platform iOS/Android with native sensor APIs |
| **Backend API** | FastAPI + Redis | FastAPI + Go microservices | Go for latency-critical telemetry ingest |
| **Auth** | JWT + bcrypt | FIDO2/Passkeys (WebAuthn) + JWT | Phishing-resistant, hardware-backed auth |
| **MFA** | Push Auth + Voice Liveness | TOTP + FaceTec Liveness SDK | Real certified liveness detection |
| **Database** | SQLite + Redis | PostgreSQL 16 + Redis Enterprise | ACID, concurrent writes, production-grade |
| **Graph DB** | Neo4j Aura Free | Neo4j Aura Professional | More nodes, GDS library for algorithms |
| **ML Models** | Heuristic z-score | Isolation Forest + XGBoost + SLRT | Real trained models with benchmark datasets |
| **ML Serving** | In-process Python | ONNX Runtime / TF Serving | Low-latency model inference |
| **Deployment** | Local laptop | Docker Compose → Cloud (GCP/AWS) | Scalable, always-on |
| **CI/CD** | Manual | GitHub Actions | Automated test + deploy |
| **Monitoring** | Console logs | Prometheus + Grafana | Real-time system health |

---

## Week 0: Post-Idea Submission Stabilization
### June 20-22 (3 days)

**Goal:** Stabilize overnight prototype, fix bugs, prepare for proper development.

### Day 1 (June 20) — Submission Day + Retrospective
- [ ] Submit idea before deadline (June 20 cutoff)
- [ ] Record a 3-minute demo video of the working prototype
- [ ] Document all known bugs and limitations
- [ ] Team retrospective: what worked, what didn't

### Day 2 (June 21) — Architecture Review
- [ ] Review your research document against the prototype
- [ ] Identify gaps between report vision and actual implementation
- [ ] Create a formal component diagram mapping all 9 system layers from the research:
  1. Deep-Tier API Payload Analysis
  2. Emulator/Cloning Detection
  3. Cryptographic Attestation (App Attest / Play Integrity)
  4. Behavioral Biometrics (continuous)
  5. Passkeys + Zero-Knowledge Proofs
  6. Graph Memory (Neo4j)
  7. Spending vs. Fraud Profiling
  8. UEBA Insider Threat Detection
  9. Federated Learning (conceptual)
- [ ] Decide: which layers get REAL implementation vs. demo simulation

### Day 3 (June 22) — Environment Upgrade
- [ ] Set up GitHub repository with proper `.gitignore`
- [ ] Initialize React project (Vite) for frontend rewrite
- [ ] Set up PostgreSQL (local Docker or cloud)
- [ ] Set up Redis (local Docker or cloud)
- [ ] Create Docker Compose for full local dev environment:
  ```yaml
  services:
    api:
      build: ./backend
      ports: ["8000:8000"]
    postgres:
      image: postgres:16
      environment:
        POSTGRES_DB: sentinel
    redis:
      image: redis:7-alpine
      ports: ["6379:6379"]
  ```
- [ ] Migrate SQLite data → PostgreSQL schema
- [ ] Set up GitHub Actions CI pipeline (lint + test)

---

## Week 1: Core Architecture & Real ML Pipeline
### June 23-29

**Goal:** Replace heuristics with real ML models. Upgrade to production database.

---

### Day 1-2 (June 23-24) — Behavioral Biometrics ML

**Train an Isolation Forest model on real keystroke data:**

#### Dataset: Keystroke Dynamics (Kaggle)
- Source: [Keystroke Dynamics Dataset](https://www.kaggle.com/datasets) — 51 subjects, 20,400 samples
- Features: flight time, dwell time per di-gram

#### Training Pipeline:
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# 1. Load and preprocess
data = pd.read_csv("keystroke_data.csv")
features = ['flight_time_mean', 'flight_time_std', 'dwell_time_mean',
            'dwell_time_std', 'typing_speed', 'digram_latency_H_E',
            'digram_latency_E_L', 'digram_latency_L_L', 'digram_latency_L_O']

# 2. Per-user model training
for user_id in data['user_id'].unique():
    user_data = data[data['user_id'] == user_id][features]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(user_data)

    model = IsolationForest(
        contamination=0.1,
        n_estimators=200,
        max_features=0.8,
        random_state=42
    )
    model.fit(X_scaled)

    # 3. Save per-user model
    joblib.dump({
        'model': model,
        'scaler': scaler,
        'baseline_stats': {
            'mean': user_data.mean().to_dict(),
            'std': user_data.std().to_dict()
        }
    }, f"models/behavioral/user_{user_id}.pkl")

# 4. Inference (real-time)
def score_user(user_id, current_features):
    model_data = joblib.load(f"models/behavioral/user_{user_id}.pkl")
    X = model_data['scaler'].transform([current_features])
    anomaly_score = model_data['model'].decision_function(X)[0]
    # Convert to 0-100 trust score
    trust = max(0, min(100, 50 + anomaly_score * 50))
    return trust
```

#### Advanced Alternative: BehaveFormer (from your research, ref [31])
- Architecture: Transformer-based with di-gram and tri-gram keystroke features
- Computes Euclidean distance between current sequence and baseline
- Paper: [arXiv:2307.11000](https://arxiv.org/pdf/2307.11000)
- Implementation: PyTorch, requires ~4 hours of training on GPU

**Decision for prototype:** Use Isolation Forest (trains in seconds, no GPU needed). Mention BehaveFormer in slides as the production architecture.

---

### Day 3-4 (June 25-26) — Transaction Fraud Detection ML

#### Dataset: PaySim Synthetic Financial Dataset
- Source: [Kaggle PaySim](https://www.kaggle.com/datasets/ealaxi/paysim1) — 6.3M transactions
- Columns: `type, amount, nameOrig, oldbalanceOrg, newbalanceOrig, nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud`

#### Training Pipeline:
```python
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import pandas as pd

# 1. Load PaySim
df = pd.read_csv("PS_20174392719_1491204439457_log.csv")

# 2. Feature engineering
df['amount_ratio'] = df['amount'] / (df['oldbalanceOrg'] + 1)
df['balance_change_orig'] = df['oldbalanceOrg'] - df['newbalanceOrig']
df['balance_change_dest'] = df['newbalanceDest'] - df['oldbalanceDest']
df['is_large_transfer'] = (df['amount'] > df['oldbalanceOrg'] * 0.5).astype(int)
df['hour'] = df['step'] % 24
df['type_encoded'] = df['type'].map({
    'CASH_IN': 0, 'CASH_OUT': 1, 'DEBIT': 2,
    'PAYMENT': 3, 'TRANSFER': 4
})

features = ['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest',
            'newbalanceDest', 'amount_ratio', 'balance_change_orig',
            'balance_change_dest', 'is_large_transfer', 'hour', 'type_encoded']

X = df[features]
y = df['isFraud']

# 3. Handle class imbalance
fraud_ratio = len(y[y==0]) / len(y[y==1])  # ~773:1

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)

# 4. Train XGBoost
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.05,
    scale_pos_weight=fraud_ratio,  # Handle imbalance
    eval_metric='auc',
    use_label_encoder=False,
    tree_method='hist'  # Fast training
)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=50)

# 5. Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
print(f"AUC-ROC: {roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]):.4f}")

# Expected: AUC-ROC > 0.99 (PaySim is well-separated)

# 6. Save model
model.save_model("models/transaction_fraud.json")
```

---

### Day 5-6 (June 27-28) — Backend Service Upgrade

- [ ] Refactor FastAPI into proper service modules:
  ```
  backend/
  ├── services/
  │   ├── auth_service.py         # FIDO2 + JWT
  │   ├── telemetry_service.py    # Ingest + buffer
  │   ├── behavioral_service.py   # ML model inference
  │   ├── transaction_service.py  # XGBoost fraud scoring
  │   ├── trust_service.py        # Composite scoring
  │   ├── mfa_service.py          # TOTP + Liveness
  │   └── graph_service.py        # Neo4j queries
  ├── models/
  │   ├── behavioral/             # Per-user Isolation Forest .pkl
  │   └── transaction_fraud.json  # XGBoost model
  ├── middleware/
  │   ├── jwt_middleware.py
  │   └── rate_limiter.py
  └── utils/
      ├── crypto.py               # Hashing, token generation
      └── validators.py           # Input validation
  ```

- [ ] Add Redis for:
  - Session management (replace in-memory dict)
  - Telemetry buffering (Redis Streams for real-time ingest)
  - Trust score caching (avoid recomputation)

- [ ] Add proper error handling with custom exception classes
- [ ] Add request logging middleware
- [ ] Add rate limiting (prevent API abuse)

---

### Day 7 (June 29) — Week 1 Review & Testing
- [ ] Unit tests for trust engine (pytest)
- [ ] Integration tests for auth flow
- [ ] ML model accuracy validation
- [ ] Performance benchmark: telemetry ingest latency < 50ms
- [ ] Code review and cleanup

---

## Week 2: Advanced Features & Graph Intelligence
### June 30 - July 6

**Goal:** Implement real graph algorithms, peer group analysis, device intelligence.

---

### Day 1-2 (June 30 - July 1) — Neo4j Graph Algorithms

Upgrade from simple pattern matching to real graph algorithms:

#### Connected Components (Fraud Ring Detection)
```cypher
// Find all isolated fraud rings
CALL gds.wcc.stream('fraud-graph')
YIELD nodeId, componentId
WITH componentId, collect(gds.util.asNode(nodeId).name) AS members
WHERE size(members) > 3
RETURN componentId, members, size(members) AS ring_size
ORDER BY ring_size DESC
```

#### PageRank (Central Hub Detection)
```cypher
// Find accounts acting as central hubs for money flow
CALL gds.pageRank.stream('transaction-graph')
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS node, score
WHERE score > 0.5
RETURN node.name, node.account, score
ORDER BY score DESC
LIMIT 10
```

#### Cycle Detection (Money Laundering Loops)
```cypher
// Detect circular fund flows: A → B → C → A
MATCH path = (start:Account)-[:TRANSFER*3..6]->(start)
WHERE ALL(r IN relationships(path) WHERE r.amount > 10000)
RETURN path, length(path) AS loop_length,
       reduce(total = 0, r IN relationships(path) | total + r.amount) AS total_flow
```

#### Similarity Scoring (Device Bipartite Graphs)
```cypher
// Find users who share suspiciously many devices
MATCH (u1:User)-[:USES_DEVICE]->(d:Device)<-[:USES_DEVICE]-(u2:User)
WHERE id(u1) < id(u2)
WITH u1, u2, count(d) AS shared_devices, collect(d.imei) AS devices
WHERE shared_devices >= 2
RETURN u1.name, u2.name, shared_devices, devices
ORDER BY shared_devices DESC
```

#### AMLSim Data Integration
- Source: [IBM/AMLSim](https://github.com/IBM/AMLSim/) — synthetic AML transaction generator
- Generate realistic money laundering patterns (smuggling, circular, fan-out)
- Load into Neo4j for algorithm testing

---

### Day 3-4 (July 2-3) — Deep API Payload & Device Intelligence

Implement concepts from your research document Sections 1-3:

#### Device Fingerprint Consistency Checker
```python
class DeviceIntelligence:
    """
    Detect spoofed devices by cross-referencing hardware metadata.
    Based on research: hw.model vs IOKit discrepancies (ref [10])
    """

    DEVICE_REGISTRY = {
        "iPhone15,4": {"chip": "A17 Pro", "ram_gb": 8, "port": "USB-C", "weight_g": 187},
        "iPhone15,3": {"chip": "A16", "ram_gb": 6, "port": "Lightning", "weight_g": 171},
        # ... expand registry
    }

    def check_consistency(self, payload):
        anomalies = []

        model_id = payload.get("hw_model")
        reported_ram = payload.get("ram_gb")
        reported_port = payload.get("port_type")

        if model_id in self.DEVICE_REGISTRY:
            expected = self.DEVICE_REGISTRY[model_id]
            if reported_ram != expected["ram_gb"]:
                anomalies.append(f"RAM mismatch: reported {reported_ram}GB, expected {expected['ram_gb']}GB")
            if reported_port != expected["port"]:
                anomalies.append(f"Port mismatch: reported {reported_port}, expected {expected['port']}")

        # Check for emulator signals
        if payload.get("sensor_count", 0) == 0:
            anomalies.append("No physical sensors detected — likely emulator")

        if payload.get("battery_status") == "unknown":
            anomalies.append("No battery data — likely emulator or VM")

        return {
            "is_spoofed": len(anomalies) > 0,
            "anomalies": anomalies,
            "risk_score": min(len(anomalies) * 25, 100)
        }
```

#### Network Geolocation Verification
```python
class GeoVerifier:
    """
    Cross-reference GPS, IP geolocation, and SIM country code.
    Based on research: geo-spoofing detection (ref [3], [9])
    """

    def verify(self, gps_coords, ip_address, sim_country_code):
        ip_geo = self.ip_to_geo(ip_address)        # GeoIP2 lookup
        gps_country = self.coords_to_country(gps_coords)

        mismatches = []

        if ip_geo.country != gps_country:
            mismatches.append(f"IP country ({ip_geo.country}) ≠ GPS country ({gps_country})")

        if sim_country_code and sim_country_code != ip_geo.country_code:
            mismatches.append(f"SIM country ({sim_country_code}) ≠ IP country ({ip_geo.country_code})")

        if ip_geo.is_vpn or ip_geo.is_tor:
            mismatches.append(f"VPN/TOR detected: {ip_geo.isp}")

        return {
            "geo_consistent": len(mismatches) == 0,
            "mismatches": mismatches,
            "risk_score": min(len(mismatches) * 30, 100)
        }
```

---

### Day 5-6 (July 4-5) — Spending vs Fraud: Peer Group Analysis

Implement Break Point Analysis + Peer Group Analysis from your research (ref [51], [52]):

```python
class SpendingAnalyzer:
    """
    Compares individual spending patterns against personal history
    AND peer group baselines to distinguish legitimate unusual
    spending from fraud.
    """

    def break_point_analysis(self, user_id, new_transaction):
        """
        Individual-level anomaly detection.
        Triggers when spending deviates beyond 2σ from personal baseline.
        """
        history = self.get_user_history(user_id, days=90)

        avg_daily = history.daily_amount.mean()
        std_daily = history.daily_amount.std()
        threshold = avg_daily + (2 * std_daily)

        if new_transaction.amount > threshold:
            return {
                "break_point_triggered": True,
                "amount": new_transaction.amount,
                "threshold": threshold,
                "z_score": (new_transaction.amount - avg_daily) / std_daily
            }
        return {"break_point_triggered": False}

    def peer_group_analysis(self, user_id, new_transaction):
        """
        Compare against peer cohort to reduce false positives.
        If the user's deviation matches a broader trend (e.g., holiday
        spending), dampen the risk score.
        """
        peer_group = self.get_peer_group(user_id)  # Same age, income, region
        peer_avg = peer_group.recent_daily_avg.mean()
        peer_std = peer_group.recent_daily_avg.std()

        user_deviation = self.break_point_analysis(user_id, new_transaction)

        if user_deviation["break_point_triggered"]:
            # Is the peer group also spending more?
            peer_trend = peer_avg > (peer_group.historical_avg.mean() * 1.3)

            if peer_trend:
                # Peer group also spending more → likely seasonal, dampen risk
                return {"risk": "LOW", "reason": "Peer group trend detected"}
            else:
                # User deviating but peers aren't → suspicious
                return {"risk": "HIGH", "reason": "Individual deviation, no peer trend"}

        return {"risk": "NONE"}
```

---

### Day 7 (July 6) — Week 2 Review
- [ ] Graph algorithm accuracy on AMLSim data
- [ ] Device intelligence edge case testing
- [ ] Peer group analysis false positive rate measurement
- [ ] Integration tests for Neo4j → Trust Engine pipeline
- [ ] Performance: graph queries < 100ms

---

## Week 3: Mobile App + FIDO2/Passkeys + Insider Threat
### July 7-13

**Goal:** Build Flutter mobile app with native sensors, implement FIDO2, and build UEBA system.

---

### Day 1-3 (July 7-9) — Flutter Mobile App

```
sentinel_mobile/
├── lib/
│   ├── main.dart
│   ├── screens/
│   │   ├── login_screen.dart
│   │   ├── dashboard_screen.dart
│   │   └── mfa_challenge_screen.dart
│   ├── services/
│   │   ├── api_service.dart          # Backend HTTP client
│   │   ├── telemetry_service.dart    # Sensor data collection
│   │   ├── biometric_service.dart    # Face/fingerprint
│   │   └── device_info_service.dart  # Device fingerprinting
│   ├── widgets/
│   │   ├── trust_gauge.dart          # Animated trust circle
│   │   └── blur_overlay.dart         # Silent lock animation
│   └── models/
│       ├── user.dart
│       └── telemetry_data.dart
├── android/
│   └── app/src/main/
│       └── kotlin/.../SensorPlugin.kt  # Native sensor bridge
└── ios/
    └── Runner/
        └── SensorPlugin.swift           # Native sensor bridge
```

**Native sensor APIs to use:**
```dart
// Flutter sensor packages
import 'package:sensors_plus/sensors_plus.dart';    // Accelerometer, Gyroscope
import 'package:local_auth/local_auth.dart';        // Biometric auth
import 'package:device_info_plus/device_info_plus.dart';  // Device fingerprint

class TelemetryService {
  // Collect accelerometer data (device holding angle)
  void startAccelerometer() {
    accelerometerEvents.listen((event) {
      // event.x, event.y, event.z → 3D device orientation
      _deviceAngleBuffer.add({
        'x': event.x, 'y': event.y, 'z': event.z,
        'timestamp': DateTime.now().millisecondsSinceEpoch
      });
    });
  }

  // Collect gyroscope data (rotation rate)
  void startGyroscope() {
    gyroscopeEvents.listen((event) {
      // Micro-tremors unique to each user's hand
      _gyroBuffer.add({
        'x': event.x, 'y': event.y, 'z': event.z,
        'timestamp': DateTime.now().millisecondsSinceEpoch
      });
    });
  }

  // Touch pressure (Android only with RawGestureDetector)
  void captureTouchPressure(PointerEvent event) {
    _touchBuffer.add({
      'pressure': event.pressure,          // 0.0 - 1.0
      'radiusMajor': event.radiusMajor,    // Contact area
      'position': {'x': event.position.dx, 'y': event.position.dy}
    });
  }
}
```

---

### Day 4-5 (July 10-11) — FIDO2/WebAuthn Passkeys

Replace password-based auth with phishing-resistant passkeys:

**Backend (Python `py_webauthn` library):**
```python
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)

# Registration
@router.post("/api/auth/passkey/register")
async def register_passkey(user_id: int):
    options = generate_registration_options(
        rp_id="sentinel.armadillo.dev",
        rp_name="Project Sentinel",
        user_id=str(user_id).encode(),
        user_name=user.username,
        attestation="direct",
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
    )
    return options

# Authentication
@router.post("/api/auth/passkey/authenticate")
async def authenticate_passkey(credential: dict):
    verification = verify_authentication_response(
        credential=credential,
        expected_challenge=stored_challenge,
        expected_rp_id="sentinel.armadillo.dev",
        expected_origin="https://sentinel.armadillo.dev",
        credential_public_key=stored_public_key,
        credential_current_sign_count=stored_sign_count,
    )
    # Issue JWT + session
    return {"token": create_jwt(user_id), "session_id": new_session_id}
```

**Frontend (WebAuthn API):**
```javascript
// Registration
const credential = await navigator.credentials.create({
    publicKey: registrationOptions
});

// Authentication (passkey login — no password!)
const assertion = await navigator.credentials.get({
    publicKey: authenticationOptions
});
```

**Why this matters (from your research ref [35]-[38]):**
> *"The private key never leaves the physical device... large-scale credential stuffing, server-side data breaches, and traditional phishing campaigns are rendered technologically obsolete."*

---

### Day 6-7 (July 12-13) — Insider Threat / UEBA Engine

Build the User and Entity Behavior Analytics system from your research (ref [56]-[58]):

```python
class UEBAEngine:
    """
    Monitors internal employee actions for insider threat detection.
    Creates per-role behavioral baselines and flags deviations.
    """

    ROLE_BASELINES = {
        "BANKER": {
            "normal_hours": (8, 18),           # 8 AM - 6 PM
            "max_daily_queries": 50,
            "max_hnw_access_without_ticket": 0,
            "max_bulk_export_records": 100,
        },
        "IT_ADMIN": {
            "normal_hours": (7, 22),
            "max_config_changes_per_day": 5,
            "max_ghost_accounts_created": 0,
            "allowed_access_segments": ["DEV", "STAGING"],
        }
    }

    def analyze_action(self, employee, action):
        baseline = self.ROLE_BASELINES[employee.role]
        alerts = []

        # Time-based anomaly
        if not (baseline["normal_hours"][0] <= action.hour <= baseline["normal_hours"][1]):
            alerts.append({
                "type": "OFF_HOURS_ACCESS",
                "severity": "HIGH",
                "detail": f"{employee.name} accessed {action.resource} at {action.hour}:00"
            })

        # Volume-based anomaly
        if action.type == "BULK_EXPORT" and action.record_count > baseline.get("max_bulk_export_records", 100):
            alerts.append({
                "type": "DATA_EXFILTRATION",
                "severity": "CRITICAL",
                "detail": f"{employee.name} exported {action.record_count} records"
            })

        # Lateral movement detection
        if employee.role == "IT_ADMIN" and action.target_segment not in baseline["allowed_access_segments"]:
            alerts.append({
                "type": "LATERAL_MOVEMENT",
                "severity": "CRITICAL",
                "detail": f"{employee.name} accessed {action.target_segment} (not authorized)"
            })

        return alerts
```

---

## Week 4: Integration Testing & Security Hardening
### July 14-20

**Goal:** End-to-end integration, security audit, DPDP Act compliance, performance optimization.

---

### Day 1-2 (July 14-15) — End-to-End Integration Testing

```python
# Test scenarios (pytest)

def test_legitimate_user_flow():
    """Full flow: register → login → use app → trust stays high"""
    token = register_and_login("legitimate_user")
    for _ in range(10):
        send_telemetry(token, NORMAL_TYPING_PATTERN)
    score = get_trust_score(token)
    assert score > 85
    assert get_decision(token) == "ALLOW"

def test_account_takeover_detection():
    """Different person types → trust drops → MFA triggered"""
    token = login("legitimate_user")
    # Establish baseline
    for _ in range(5):
        send_telemetry(token, NORMAL_TYPING_PATTERN)
    # Simulate attacker
    for _ in range(5):
        send_telemetry(token, DIFFERENT_TYPING_PATTERN)
    score = get_trust_score(token)
    assert score < 85
    assert get_decision(token) == "STEP_UP"

def test_mfa_recovery():
    """After successful MFA, trust recovers"""
    token = login("legitimate_user")
    trigger_step_up(token)
    verify_totp(token, generate_valid_totp())
    score = get_trust_score(token)
    assert score > 80
    assert get_decision(token) == "ALLOW"

def test_fraud_ring_detection():
    """Neo4j identifies shared device clusters"""
    result = query_fraud_rings()
    assert len(result.rings) >= 1
    assert result.rings[0].size >= 5

def test_insider_threat_alert():
    """Banker accessing records at 2 AM triggers CRITICAL alert"""
    alerts = ueba_engine.analyze_action(
        employee=banker, action=Action(hour=2, type="QUERY_HNW")
    )
    assert any(a["severity"] == "CRITICAL" for a in alerts)
```

---

### Day 3-4 (July 16-17) — Security Hardening

- [ ] **HTTPS everywhere:** TLS certificates (Let's Encrypt)
- [ ] **Input sanitization:** SQL injection prevention (parameterized queries)
- [ ] **Rate limiting:** Max 100 requests/min per user, Max 10 login attempts/hour
- [ ] **JWT hardening:** Short expiry (15 min), refresh tokens, token rotation
- [ ] **CORS lockdown:** Only allow specific origins in production
- [ ] **CSP headers:** Content-Security-Policy to prevent XSS
- [ ] **Dependency audit:** `pip audit` + `npm audit` for CVEs
- [ ] **Secret management:** Environment variables, never committed to git
- [ ] **API key rotation:** Neo4j, any 3rd party services

---

### Day 5-6 (July 18-19) — DPDP Act 2023 Compliance

Ensure alignment with the Digital Personal Data Protection Act:

| DPDP Requirement | Sentinel Implementation |
|---|---|
| **Consent** | Users explicitly consent to behavioral monitoring during registration |
| **Purpose Limitation** | Telemetry used ONLY for security scoring, not marketing |
| **Data Minimization** | Raw keystrokes processed on-device/edge; only anonymized trust vector sent to server |
| **Storage Limitation** | Behavioral baselines auto-purge after 90 days of inactivity |
| **Right to Erasure** | DELETE `/api/user/data` endpoint removes all user telemetry + baselines |
| **Data Principal Rights** | GET `/api/user/data-export` returns all stored personal data as JSON |
| **Breach Notification** | Automated email + SOC alert within 72 hours of any detected breach |
| **Cross-border Transfer** | Neo4j Aura deployed in India region; no data leaves Indian jurisdiction |

---

### Day 7 (July 20) — Performance Optimization

Performance targets:

| Metric | Target | How to Achieve |
|---|---|---|
| Telemetry ingest latency | < 30ms | Redis Streams buffering |
| Trust score computation | < 50ms | Pre-loaded ML models + cached sub-scores |
| Graph query response | < 100ms | Neo4j GDS projected graphs + index tuning |
| Page load time | < 2 seconds | Code splitting, lazy loading, CDN |
| API throughput | > 1000 req/sec | Uvicorn workers, connection pooling |

---

## Week 5: Final Polish, Demo Video, Deployment
### July 21-26 (Prototype Submission Deadline: July 26)

---

### Day 1-2 (July 21-22) — UI/UX Final Polish

**React Frontend Overhaul:**
- [ ] Animated onboarding flow
- [ ] Dashboard micro-interactions (hover effects, transitions)
- [ ] Trust score gauge with particle effects
- [ ] Real-time alert notifications (WebSocket)
- [ ] Dark/Light mode toggle
- [ ] Mobile-responsive design
- [ ] Accessibility compliance (ARIA labels, keyboard navigation)
- [ ] Armadillo team branding throughout

---

### Day 3-4 (July 23-24) — Demo Video Production

Record a **5-minute demo video** covering:

1. **Problem Statement** (30 sec): Static auth fails, $4.61 per $1 of fraud
2. **Architecture Overview** (1 min): 3-layer diagram walkthrough
3. **Live Demo — Account Takeover** (2 min): Trust score drop + adaptive MFA
4. **Live Demo — Fraud Ring** (1 min): Neo4j graph visualization
5. **Business Impact** (30 sec): OTP cost savings, DPDP compliance, ROI

**Tools:** OBS Studio for recording, DaVinci Resolve for editing

---

### Day 5 (July 25) — Cloud Deployment

Deploy to cloud for jury access:

```yaml
# docker-compose.prod.yml
services:
  traefik:
    image: traefik:v3
    # Reverse proxy + auto-HTTPS

  api:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379
      - NEO4J_URI=neo4j+s://...
    deploy:
      replicas: 2

  frontend:
    build: ./frontend
    # Served via Nginx

  postgres:
    image: postgres:16
    volumes:
      - pg_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
```

**Deployment options:**
- **Option A:** GCP Cloud Run (serverless, auto-scaling)
- **Option B:** AWS EC2 + Docker Compose (simple, predictable)
- **Option C:** Railway.app (easiest, free tier available)

---

### Day 6 (July 26) — Submission Day

- [ ] Final end-to-end test on deployed instance
- [ ] Submit prototype URL + source code + demo video
- [ ] Submit documentation:
  - Project Sentinel Report (updated)
  - Banking Fraud Detection Research paper
  - Architecture diagrams (all 4 versions)
  - ML model evaluation metrics
  - DPDP compliance statement
- [ ] Prepare for jury Q&A:
  - Technical deep-dive questions
  - Scalability questions
  - Compliance questions
  - Business impact quantification

---

## Feature Completeness Matrix (Full Build)

| Feature (from Research Paper) | Prototype (June 19) | Full Build (July 26) | Production |
|---|---|---|---|
| **Keystroke dynamics** | ✅ Heuristic z-score | ✅ Isolation Forest ML | BehaveFormer Transformer |
| **Mouse movement analysis** | ✅ Basic velocity/straightness | ✅ Full trajectory analysis | Deep learning on trajectories |
| **Device fingerprinting** | ✅ Browser-level | ✅ + Hardware consistency checks | + TrueDevice SDK integration |
| **Emulator detection** | ❌ Mentioned only | ✅ Sensor-based detection | + RASP integration |
| **App Attest / Play Integrity** | ❌ Mentioned only | 🟡 Conceptual demo | ✅ Full hardware attestation |
| **FIDO2 / Passkeys** | ❌ Password-based | ✅ WebAuthn implementation | ✅ + Passkey sync across devices |
| **Zero-Knowledge Proofs** | ❌ Mentioned only | 🟡 Conceptual demo | ✅ ZKP-based auth (BAuth-ZKP) |
| **Adaptive MFA** | ✅ TOTP + simulated face | ✅ TOTP + real face liveness | + FaceTec certified liveness |
| **Trust Score Engine** | ✅ 4 sub-scores, heuristic | ✅ ML-powered, 6 sub-scores | + Real-time Bayesian updating |
| **Neo4j graph queries** | ✅ Simple pattern matching | ✅ GDS algorithms (PageRank, WCC, Cycles) | + Streaming graph updates |
| **Fraud ring detection** | ✅ Pre-seeded demo data | ✅ AMLSim + PaySim trained | + Live transaction graph |
| **Transaction fraud ML** | ❌ Not implemented | ✅ XGBoost on PaySim | + Real-time feature store |
| **Peer Group Analysis** | ❌ Not implemented | ✅ Break point + peer cohort | + Dynamic clustering |
| **Insider threat / UEBA** | ❌ Mentioned only | ✅ Rule-based + role baselines | + ML-based UEBA |
| **Federated Learning** | ❌ Concept only | 🟡 Demo with Flower framework | ✅ Multi-bank FL network |
| **DPDP Act compliance** | 🟡 Edge processing claim | ✅ Full compliance documentation | ✅ Auditable compliance |
| **Mobile app** | ❌ Web only | ✅ Flutter with native sensors | ✅ + Gyroscope + touch pressure |
| **SOC dashboard** | ✅ Basic alerts | ✅ + Real-time WebSocket + graph viz | + SIEM integration |
| **Docker deployment** | ❌ Local only | ✅ Docker Compose + cloud | Kubernetes |

---

## Datasets & Training Summary

| Dataset | Used For | Size | Source | Week |
|---|---|---|---|---|
| **Keystroke Dynamics (Kaggle)** | Behavioral biometrics (Isolation Forest) | 51 users, 20.4K samples | [Kaggle](https://www.kaggle.com/datasets) | Week 1 |
| **PaySim** | Transaction fraud (XGBoost) | 6.3M transactions | [Kaggle](https://www.kaggle.com/datasets/ealaxi/paysim1) | Week 1 |
| **AMLSim** | Money laundering graph patterns | Synthetic, configurable | [IBM/AMLSim](https://github.com/IBM/AMLSim/) | Week 2 |
| **Elliptic Bitcoin** | Graph neural network fraud | 203K nodes, 234K edges | [Kaggle](https://www.kaggle.com/datasets/ellipticco/elliptic-data-set) | Week 2 |
| **DGraphFin** | Social graph anomaly detection | 3.7M nodes | [GitHub](https://github.com/storyandwine/GEARSage-DGraphFin) | Week 2 |
| **Balabit Mouse Dynamics** | Mouse behavior authentication | Mouse trajectory data | Research dataset | Week 3 |
| **CERT Insider Threat** | UEBA insider threat training | Enterprise simulation | Carnegie Mellon | Week 3 |

---

## Key Milestones

| Date | Milestone | Deliverable |
|---|---|---|
| June 19 | Prototype Demo | Working web app with live behavioral detection |
| June 20 | Idea Submission | Report + prototype + demo video |
| June 25 | Shortlist Announcement | Check if selected for next round |
| June 29 | ML Models Trained | Isolation Forest + XGBoost models validated |
| July 6 | Graph Intelligence Live | Neo4j GDS algorithms + AMLSim data integrated |
| July 13 | Mobile App + FIDO2 | Flutter app with sensor telemetry + Passkey auth |
| July 20 | Security Audit Complete | DPDP compliance + penetration testing |
| July 26 | **Prototype Submission** | Full system deployed to cloud + demo video |
| Aug 1-7 | Jury Evaluation | Prepare for live Q&A and demo |

---

> **💡 Strategy:** The June 19 prototype wins the shortlist. The July 26 prototype wins the hackathon.
> Focus the overnight build on the "wow" demo moments. Focus the 1-month build on making it real.
