"""
Project Sentinel — Neo4j Seed Script
Populates Neo4j Aura with realistic fraud ring data for the demo video.
Run this ONCE after setting NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD in .env
"""
import os
import sys

# Load .env
from pathlib import Path
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

if not NEO4J_URI or "xxxxxxxx" in NEO4J_URI:
    print("ERROR: Please set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in backend/.env first!")
    print("Get a free instance at: https://neo4j.com/cloud/aura-free/")
    sys.exit(1)

try:
    from neo4j import GraphDatabase
except ImportError:
    print("Installing neo4j driver...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "neo4j"])
    from neo4j import GraphDatabase


def seed_neo4j():
    print(f"Connecting to Neo4j: {NEO4J_URI}")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    print("[OK] Connected to Neo4j!")

    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        print("[OK] Cleared old data.")

        # ─── Ring 1: The Mule Network ───────────────────────────
        session.run("""
            // Central victim
            CREATE (victim:User {name: 'Priyansh Patel', account_no: 'BOB-7821-XXXX', flagged: false, risk_level: 'LOW'})
            
            // Attacker who took over victim's session
            CREATE (attacker:User {name: 'attacker_x9', account_no: 'FAKE-0091', flagged: true, risk_level: 'CRITICAL'})
            
            // Mule accounts
            CREATE (mule1:User {name: 'Rajesh K.', account_no: 'MULE-4401', flagged: true, risk_level: 'HIGH'})
            CREATE (mule2:User {name: 'Sunil M.', account_no: 'MULE-4402', flagged: true, risk_level: 'HIGH'})
            CREATE (mule3:User {name: 'Deepak R.', account_no: 'MULE-4403', flagged: true, risk_level: 'HIGH'})
            CREATE (mule4:User {name: 'Amit P.', account_no: 'MULE-4404', flagged: true, risk_level: 'CRITICAL'})
            
            // Devices
            CREATE (dev1:Device {model: 'Chrome/Win11', imei: 'A4F2-BC91-XX', os: 'Windows 11'})
            CREATE (dev2:Device {model: 'Samsung s24fe', imei: '8B2C-DD01-XX', os: 'Android 15'})
            CREATE (dev3:Device {model: 'Firefox/Linux', imei: 'C1E8-FF02-XX', os: 'Ubuntu 24.04'})
            
            // IPs
            CREATE (ip1:IP {address: '49.36.182.xx', is_vpn: false, geo_city: 'Ahmedabad'})
            CREATE (vpn1:IP {address: '103.21.34.xx', is_vpn: true, geo_city: 'Amsterdam (VPN)'})
            CREATE (vpn2:IP {address: '185.56.12.xx', is_vpn: true, geo_city: 'Frankfurt (VPN)'})
            
            // Accounts
            CREATE (acct1:Account {number: 'BOB-7821-XXXX', bank: 'Bank of Baroda', type: 'Savings'})
            CREATE (muleAcct:Account {number: 'MULE-9981', bank: 'Unknown FinTech', type: 'Current'})
            
            // Transactions
            CREATE (txn1:Transaction {id: 'TXN-50001', amount: 50000, type: 'NEFT', timestamp: '2026-06-18T02:14:00'})
            CREATE (txn2:Transaction {id: 'TXN-50002', amount: 25000, type: 'UPI', timestamp: '2026-06-18T02:16:00'})
            CREATE (txn3:Transaction {id: 'TXN-50003', amount: 12000, type: 'IMPS', timestamp: '2026-06-18T02:18:00'})
            
            // ─── Relationships ─────────────────────────────────
            // Victim's normal connections
            CREATE (victim)-[:USES_DEVICE]->(dev1)
            CREATE (victim)-[:CONNECTS_FROM]->(ip1)
            CREATE (victim)-[:OWNS]->(acct1)
            
            // ATO Attack Path (attacker hijacked victim's device)
            CREATE (attacker)-[:USES_DEVICE]->(dev1)
            CREATE (attacker)-[:CONNECTS_FROM]->(vpn1)
            CREATE (attacker)-[:MADE]->(txn1)
            CREATE (txn1)-[:TO]->(muleAcct)
            
            // Mule Ring (all connect from same VPN, same device, to same account)
            CREATE (mule1)-[:USES_DEVICE]->(dev2)
            CREATE (mule1)-[:CONNECTS_FROM]->(vpn1)
            CREATE (mule1)-[:MADE]->(txn2)
            CREATE (txn2)-[:TO]->(muleAcct)
            
            CREATE (mule2)-[:USES_DEVICE]->(dev2)
            CREATE (mule2)-[:CONNECTS_FROM]->(vpn1)
            CREATE (mule2)-[:MADE]->(txn3)
            CREATE (txn3)-[:TO]->(muleAcct)
            
            CREATE (mule3)-[:USES_DEVICE]->(dev3)
            CREATE (mule3)-[:CONNECTS_FROM]->(vpn2)
            CREATE (mule3)-[:TRANSFERS_TO]->(muleAcct)
            
            CREATE (mule4)-[:USES_DEVICE]->(dev3)
            CREATE (mule4)-[:CONNECTS_FROM]->(vpn2)
            CREATE (mule4)-[:TRANSFERS_TO]->(muleAcct)
            
            // Shared KYC link (mules used same PAN/Aadhaar)
            CREATE (mule1)-[:LINKED_TO {reason: 'Same PAN'}]->(mule2)
            CREATE (mule3)-[:LINKED_TO {reason: 'Same Aadhaar'}]->(mule4)
        """)

        # ─── Ring 2: Insider Threat ─────────────────────────────
        session.run("""
            CREATE (insider:User {name: 'Vikram (Employee)', account_no: 'EMP-0042', flagged: true, risk_level: 'CRITICAL'})
            CREATE (hnw1:User {name: 'HNW Client Arora', account_no: 'BOB-PREM-8801', flagged: false, risk_level: 'LOW'})
            CREATE (hnw2:User {name: 'HNW Client Mehta', account_no: 'BOB-PREM-8802', flagged: false, risk_level: 'LOW'})
            CREATE (branchIP:IP {address: '10.0.5.xx', is_vpn: false, geo_city: 'Gandhinagar Branch'})
            
            CREATE (insider)-[:CONNECTS_FROM]->(branchIP)
            CREATE (insider)-[:ACCESSED_PII]->(hnw1)
            CREATE (insider)-[:ACCESSED_PII]->(hnw2)
        """)

        # ─── Ring 3: Clean Users (contrast) ─────────────────────
        session.run("""
            CREATE (clean1:User {name: 'Ananya S.', account_no: 'BOB-3301', flagged: false, risk_level: 'LOW'})
            CREATE (clean2:User {name: 'Rohit V.', account_no: 'BOB-3302', flagged: false, risk_level: 'LOW'})
            CREATE (cleanDev:Device {model: 'iPhone 15', imei: 'AAPL-1234-XX', os: 'iOS 18'})
            CREATE (cleanIP:IP {address: '103.50.xx.xx', is_vpn: false, geo_city: 'Mumbai'})
            
            CREATE (clean1)-[:USES_DEVICE]->(cleanDev)
            CREATE (clean1)-[:CONNECTS_FROM]->(cleanIP)
            CREATE (clean2)-[:CONNECTS_FROM]->(cleanIP)
        """)

    print("\n✅ Neo4j seeded successfully!")
    print("   • Ring 1: Mule Network (6 users, 3 devices, 3 IPs, 3 txns)")
    print("   • Ring 2: Insider Threat (1 employee, 2 HNW clients)")
    print("   • Ring 3: Clean Users (2 legitimate accounts)")
    print("\nRefresh http://localhost:5173/soc to see the live graph!")

    driver.close()


if __name__ == "__main__":
    seed_neo4j()
