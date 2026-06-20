"""
Project Sentinel — Graph Routes
Returns Neo4j fraud ring data for visualization.
Connects to real Neo4j Aura instance; falls back to mock data gracefully.
"""
from fastapi import APIRouter, Depends
from auth.routes import get_current_user
import os

router = APIRouter()

# ─── Neo4j Connection ───────────────────────────────────────────────
NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

_driver = None

def get_neo4j_driver():
    """Lazy-initialize Neo4j driver (only when first needed)."""
    global _driver
    if _driver is None and NEO4J_URI and "xxxxxxxx" not in NEO4J_URI:
        try:
            from neo4j import GraphDatabase
            _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            _driver.verify_connectivity()
            print("[OK] Neo4j connected:", NEO4J_URI)
        except Exception as e:
            print(f"[WARN] Neo4j connection failed: {e}. Using mock data.")
            _driver = None
    return _driver


def query_neo4j_graph():
    """Query real Neo4j for fraud ring nodes and edges."""
    driver = get_neo4j_driver()
    if not driver:
        return None

    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            # Fetch all nodes
            node_result = session.run("""
                MATCH (n)
                RETURN id(n) AS id, labels(n) AS labels, properties(n) AS props
            """)
            nodes = []
            for record in node_result:
                node_id = record["id"]
                labels = record["labels"]
                props = dict(record["props"])
                label_type = labels[0] if labels else "Unknown"

                # Determine group for vis.js coloring
                if label_type == "User":
                    group = "flagged_user" if props.get("flagged") else "user"
                    display = props.get("name", f"User-{node_id}")
                elif label_type == "Device":
                    group = "device"
                    display = f"Device: {props.get('model', 'Unknown')}"
                elif label_type == "IP":
                    group = "flagged_ip" if props.get("is_vpn") else "ip"
                    display = f"IP: {props.get('address', '?.?.?.?')}"
                elif label_type == "Account":
                    group = "account"
                    display = f"Acct: {props.get('number', 'XXXX')}"
                elif label_type == "Transaction":
                    group = "transaction"
                    display = f"₹{props.get('amount', 0)}"
                else:
                    group = "unknown"
                    display = str(props)

                title_parts = [f"{k}: {v}" for k, v in props.items()]
                nodes.append({
                    "id": node_id,
                    "label": display,
                    "group": group,
                    "title": f"{label_type} | " + ", ".join(title_parts)
                })

            # Fetch all relationships
            edge_result = session.run("""
                MATCH (a)-[r]->(b)
                RETURN id(a) AS from_id, id(b) AS to_id, type(r) AS rel_type, properties(r) AS props
            """)
            edges = []
            for record in edge_result:
                edge = {
                    "from": record["from_id"],
                    "to": record["to_id"],
                    "label": record["rel_type"]
                }
                # Highlight suspicious edges in red
                rel = record["rel_type"]
                if rel in ("USES_DEVICE", "LINKED_TO") and any(
                    n["group"] == "flagged_user" for n in nodes
                    if n["id"] in (record["from_id"], record["to_id"])
                ):
                    edge["color"] = {"color": "#ff4444"}
                edges.append(edge)

        return {"nodes": nodes, "edges": edges}
    except Exception as e:
        print(f"[WARN] Neo4j query failed: {e}")
        return None


# ─── Fallback Mock Data ─────────────────────────────────────────────
MOCK_GRAPH_DATA = {
    "nodes": [
        {"id": 1, "label": "priyansh (Victim)", "group": "user", "title": "User: priyansh | Account: XXXX-7821"},
        {"id": 2, "label": "attacker_x9", "group": "flagged_user", "title": "User: attacker_x9 | Risk: HIGH"},
        {"id": 3, "label": "Device: Chrome/Win11", "group": "device", "title": "IMEI: A4F2-BC91-XX"},
        {"id": 4, "label": "IP: 49.36.x.x", "group": "ip", "title": "ISP: Jio, Vadodara"},
        {"id": 5, "label": "Acct: XXXX-4521", "group": "account", "title": "Bank of Baroda Savings"},
        {"id": 6, "label": "Acct: MULE-9981", "group": "account", "title": "Suspected Mule Account"},
        {"id": 7, "label": "mule_01", "group": "flagged_user", "title": "User: mule_01 | Risk: CRITICAL"},
        {"id": 8, "label": "mule_02", "group": "flagged_user", "title": "User: mule_02 | Risk: HIGH"},
        {"id": 9, "label": "VPN: 103.21.x.x", "group": "flagged_ip", "title": "Known VPN Exit Node (ProtonVPN)"},
        {"id": 10, "label": "₹50,000 Transfer", "group": "transaction", "title": "Txn: ₹50,000 | Under Duress"},
        {"id": 11, "label": "insider_emp", "group": "flagged_user", "title": "User: insider_emp | Bank Employee"},
        {"id": 12, "label": "Device: Samsung A52", "group": "device", "title": "IMEI: 8B2C-DD01-XX"},
    ],
    "edges": [
        # Victim's legitimate connections
        {"from": 1, "to": 3, "label": "USES_DEVICE"},
        {"from": 1, "to": 4, "label": "CONNECTS_FROM"},
        {"from": 1, "to": 5, "label": "OWNS"},

        # Attacker ATO path (RED — this is the story)
        {"from": 2, "to": 3, "label": "USES_DEVICE (ATO)", "color": {"color": "#ff4444"}},
        {"from": 2, "to": 9, "label": "CONNECTS_FROM"},
        {"from": 2, "to": 10, "label": "INITIATED", "color": {"color": "#ff4444"}},
        {"from": 10, "to": 6, "label": "SENT_TO", "color": {"color": "#ff4444"}},

        # Mule ring cluster
        {"from": 7, "to": 6, "label": "TRANSFERS_TO"},
        {"from": 8, "to": 6, "label": "TRANSFERS_TO"},
        {"from": 7, "to": 9, "label": "CONNECTS_FROM"},
        {"from": 8, "to": 9, "label": "CONNECTS_FROM"},
        {"from": 7, "to": 12, "label": "USES_DEVICE"},
        {"from": 8, "to": 12, "label": "USES_DEVICE", "color": {"color": "#ff4444"}},

        # Insider threat
        {"from": 11, "to": 5, "label": "ACCESSED_PII", "color": {"color": "#ff4444"}},
        {"from": 11, "to": 4, "label": "CONNECTS_FROM"},
    ]
}


@router.get("/fraud-ring")
async def get_fraud_ring(user: dict = Depends(get_current_user)):
    """
    Returns the fraud ring graph.
    Tries real Neo4j first; falls back to realistic mock data.
    """
    live_data = query_neo4j_graph()
    if live_data and len(live_data.get("nodes", [])) > 0:
        return live_data
    return MOCK_GRAPH_DATA
