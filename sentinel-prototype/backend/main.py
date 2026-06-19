"""
Project Sentinel — Main FastAPI Application
Entry point for the backend server.
"""
import sys
from pathlib import Path

# Ensure backend directory is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from auth.routes import router as auth_router
from telemetry.routes import router as telemetry_router
from mfa.routes import router as mfa_router
from soc.routes import router as soc_router
from graph.routes import router as graph_router
from payments.routes import router as payments_router


# ─── Initialize App ────────────────────────────────────────────────

app = FastAPI(
    title="Project Sentinel API",
    description="Continuous Identity Trust & Adaptive MFA — Team Armadillo",
    version="1.0.0",
)

# ─── CORS ───────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ────────────────────────────────────────────────────────

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(telemetry_router, prefix="/api/telemetry", tags=["Telemetry"])
app.include_router(mfa_router, prefix="/api/mfa", tags=["MFA"])
app.include_router(soc_router, prefix="/api/soc", tags=["SOC Dashboard"])
app.include_router(graph_router, prefix="/api/graph", tags=["Fraud Graph"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])


# ─── Startup ────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    """Initialize database on server start."""
    init_db()
    print("[OK] Project Sentinel API is running!")
    print("   Docs: http://localhost:8000/docs")


# ─── Health Check ───────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "project": "Sentinel", "team": "Armadillo"}
