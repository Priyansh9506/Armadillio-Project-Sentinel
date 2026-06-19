"""
Project Sentinel — Configuration
Loads environment variables and provides app-wide constants.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "sentinel-armadillo-secret-key-2026")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Neo4j Settings
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://xxxxxxxx.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password-here")

# Redis Settings
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# SQLite Database
DB_PATH = BASE_DIR / "sentinel.db"

# Trust Score Thresholds
TRUST_ALLOW_THRESHOLD = 10
TRUST_STEP_UP_THRESHOLD = 5

# Telemetry
TELEMETRY_WINDOW_SECONDS = 3
BASELINE_ENROLLMENT_SECONDS = 30

# Duress PIN (Panic Button)
DURESS_PIN_SUFFIX = "9999"
