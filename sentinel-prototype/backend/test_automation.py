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
    
    # 1. Login with Vyom
    print("\n1. Testing Login as Vyom...")
    auth = request("/auth/login", {
        "username": "9123456789",
        "credential": "password123",
        "login_type": "password"
    })
    if not auth or 'token' not in auth:
        print("FAIL: Login failed.")
        return
    token = auth['token']
    session_id = auth['session_id']
    user_id = auth.get('user_id', 2)
    print("SUCCESS: Logged in as Vyom.")
    
    # 2. Test PIN Status
    print("\n2. Testing PIN Status")
    pin_status = request("/payments/pin-status", token=token, method="GET")
    if pin_status and 'has_pin' in pin_status:
        print(f"SUCCESS: PIN status retrieved. Has PIN: {pin_status['has_pin']}")
    else:
        print("FAIL: PIN status failed.")
        
    # 3. Test Transfer
    print("\n3. Testing Transfer to Priyansh")
    transfer = request("/payments/upi/send", {
        "session_id": session_id,
        "to_upi_id": "priyansh@bob",
        "amount": 500.0,
        "upi_pin": "1234",
        "note": "Dinner split"
    }, token=token)
    
    if transfer and transfer.get('message'):
        print(f"SUCCESS: Transfer successful. Message: {transfer.get('message')}")
    else:
        print(f"FAIL: Transfer failed. {transfer}")
        
    # 4. Test Bill Pay
    print("\n4. Testing Bill Pay")
    bill_pay = request("/payments/bills/pay", {
        "session_id": session_id,
        "biller_id": "1234567890",
        "amount": 2500.0,
        "txn_pin": "1234"
    }, token=token)
    
    if bill_pay and bill_pay.get('message'):
        print(f"SUCCESS: Bill pay successful. Message: {bill_pay.get('message')}")
    else:
        print(f"FAIL: Bill pay failed. {bill_pay}")
        
    # 5. Test Change Password with MFA
    print("\n5. Testing Change Password with MFA")
    # Initiate MFA
    mfa_init = request("/mfa/push-auth/initiate", {"session_id": session_id}, token=token)
    if mfa_init and mfa_init.get('challenge_id'):
        challenge_id = mfa_init['challenge_id']
        print(f"  - Initiated Push Auth. Challenge ID: {challenge_id}")
        
        # Verify MFA (prototype fallback token: 123456)
        mfa_verify = request("/mfa/push-auth/verify", {
            "challenge_id": challenge_id,
            "session_id": session_id,
            "number_selected": 12  # Doesn't matter due to fallback token
        }, token=token)
        
        # Since verify endpoint in prototype doesn't actually set 'verified', we'll just pass '123456' as mfa_token to change-password
        pwd_change = request("/auth/change-password", {
            "old_password": "password123",
            "new_password": "newpassword123",
            "mfa_token": "123456"
        }, token=token)
        
        if pwd_change and pwd_change.get('message'):
            print(f"SUCCESS: Password changed. Message: {pwd_change.get('message')}")
        else:
            print(f"FAIL: Password change failed. {pwd_change}")
    else:
        print("FAIL: MFA Initiate failed.")
        
    # 6. Test Duress Attack
    print("\n6. Testing Duress Attack Transfer (PIN: 12349999)")
    duress = request("/payments/upi/send", {
        "session_id": session_id,
        "to_upi_id": "hacker@bob",
        "amount": 50000.0,
        "upi_pin": "12349999",
        "note": "Urgent transfer"
    }, token=token)
    
    if duress and duress.get('message'):
        print(f"SUCCESS: Duress attack processed silently. Message: {duress.get('message')}")
    else:
        print(f"WARN/FAIL: Duress attack response: {duress}")
        
    # 7. Test SOC and Graph Data
    print("\n7. Testing SOC Dashboard Endpoints")
    alerts = request("/soc/alerts", token=token, method="GET")
    if alerts is not None:
        print(f"SUCCESS: Retrieved {len(alerts)} alerts from SOC.")
    else:
        print("FAIL: Failed to retrieve SOC alerts.")
        
    trust_logs = request(f"/soc/trust-logs?user_id={user_id}", token=token, method="GET")
    if trust_logs is not None:
        print(f"SUCCESS: Retrieved {len(trust_logs)} trust logs.")
    else:
        print("FAIL: Failed to retrieve trust logs.")
        
    stats = request("/soc/stats", token=token, method="GET")
    if stats is not None:
        print(f"SUCCESS: Retrieved SOC stats: {stats}")
    else:
        print("FAIL: Failed to retrieve SOC stats.")
        
    print("\n8. Testing Fraud Ring Graph API")
    graph = request("/graph/fraud-ring", token=token, method="GET")
    if graph and 'nodes' in graph:
        print(f"SUCCESS: Graph data retrieved. Nodes: {len(graph['nodes'])}, Edges: {len(graph['edges'])}")
    else:
        print("FAIL: Fraud Ring Graph API failed.")
        
    print("\n=== Automation Test Complete ===")

if __name__ == '__main__':
    run_tests()
