import sys
sys.path.insert(0, ".")
from auth.routes import get_current_user
from telemetry.routes import router as t_router
from mfa.routes import router as m_router
from soc.routes import router as s_router
print("ALL IMPORTS OK")
