import urllib.request
import json
import time

BASE_URL = "http://localhost:8000/api"

def request(endpoint, payload=None, token=None, method="POST"):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(payload).encode() if payload else None
    
    if method == "GET":
        req = urllib.request.Request(f"{BASE_URL}{endpoint}", headers=headers, method="GET")
    else:
        req = urllib.request.Request(f"{BASE_URL}{endpoint}", data=data, headers=headers, method=method)
        
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP Error {e.code} on {endpoint}: {body}")
        return None
    except Exception as e:
        print(f"Error on {endpoint}: {e}")
        return None

def run_tests():
    print("=== Sentinel End-to-End Automation Test ===")
    
    # 1. Login
    print("\n1. Testing Login...")
    auth = request("/auth/login", {
        "username": "9876543210",
        "credential": "password123",
        "login_type": "password"
    })
    if not auth or 'token' not in auth:
        print("FAIL: Login failed.")
        return
    token = auth['token']
    session_id = auth['session_id']
    print("SUCCESS: Logged in as Priyansh.")
    
    # 2. Test Telemetry Ingestion
    print("\n2. Testing Telemetry Ingestion")
    telemetry = request("/telemetry/ingest", {
        "session_id": session_id,
        "keystroke_metrics": {"avg_flight_time": 150.0, "avg_dwell_time": 80.0, "typing_speed": 5.0},
        "mouse_metrics": {"avg_velocity": 300.0, "path_straightness": 0.8}
    }, token=token)
    if telemetry and 'trust_score' in telemetry:
        print(f"SUCCESS: Telemetry ingested. Trust Score: {telemetry['trust_score']}, Decision: {telemetry['decision']}")
    else:
        print("FAIL: Telemetry ingestion failed.")
        
    # 3. Test PIN Status
    print("\n3. Testing PIN Status")
    pin_status = request("/payments/pin-status", token=token, method="GET")
    if pin_status and 'has_pin' in pin_status:
        print(f"SUCCESS: PIN status retrieved. Has PIN: {pin_status['has_pin']}")
    else:
        print("FAIL: PIN status failed.")
        
    # 4. Test Transaction (UPI Transfer)
    print("\n4. Testing UPI Transaction (Normal)")
    transfer = request("/payments/upi/send", {
        "session_id": session_id,
        "to_upi_id": "vyom@bob",
        "amount": 10.0,
        "upi_pin": "123456",
        "note": "Test Automation"
    }, token=token)
    
    if transfer and transfer.get('status') == 'SUCCESS':
        print("SUCCESS: Transaction successful.")
    else:
        print(f"WARN/FAIL: Transaction response: {transfer}")
        
    # 5. Test SOC Endpoints
    print("\n5. Testing SOC Dashboard Endpoints")
    alerts = request("/soc/alerts", token=token, method="GET")
    if alerts is not None:
        print(f"SUCCESS: Retrieved {len(alerts)} alerts from SOC.")
    else:
        print("FAIL: Failed to retrieve SOC alerts.")
        
    trust_logs = request(f"/soc/trust-logs?user_id=1", token=token, method="GET")
    if trust_logs is not None:
        print(f"SUCCESS: Retrieved {len(trust_logs)} trust logs.")
    else:
        print("FAIL: Failed to retrieve trust logs.")
        
    stats = request("/soc/stats", token=token, method="GET")
    if stats is not None:
        print(f"SUCCESS: Retrieved SOC stats: {stats}")
    else:
        print("FAIL: Failed to retrieve SOC stats.")
        
    # 6. Test Fraud Ring Graph API
    print("\n6. Testing Fraud Ring Graph API")
    graph = request("/graph/fraud-ring", token=token, method="GET")
    if graph and 'nodes' in graph:
        print(f"SUCCESS: Graph data retrieved. Nodes: {len(graph['nodes'])}, Edges: {len(graph['edges'])}")
    else:
        print("FAIL: Fraud Ring Graph API failed.")
        
    print("\n=== Automation Test Complete ===")

if __name__ == '__main__':
    run_tests()
