"""
Project Sentinel — Supabase Client
Connects to Supabase PostgreSQL for cloud transaction storage.
"""
import os
from config import BASE_DIR
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_client = None

def get_supabase():
    """Returns the Supabase client singleton."""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("[WARN] Supabase credentials not set. Payments will use local DB only.")
            return None
        try:
            from supabase import create_client
            _client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("[OK] Supabase connected:", SUPABASE_URL)
        except Exception as e:
            print(f"[WARN] Supabase connection failed: {e}")
            return None
    return _client
