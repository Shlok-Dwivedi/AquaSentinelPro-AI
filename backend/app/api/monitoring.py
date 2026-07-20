import time
import psutil
import os
import logging
from fastapi import APIRouter
from supabase import Client
from app.services.db_service import get_supabase_unauth
from app.crud.monitoring_crud import check_db_health
from app.config import settings

logger = logging.getLogger("aquasentinel")

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

# Server start timestamp for uptime calculation
START_TIME = time.time()

@router.get("/health")
def health_check():
    """Verifies service readiness, database connectivity, and configuration states."""
    supabase = get_supabase_unauth()
    is_healthy = check_db_health(supabase)
    db_status = "healthy" if is_healthy else "unhealthy"
        
    gemini_status = "unconfigured (mock fallbacks active)"
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY not in ["YOUR_GEMINI_API_KEY_HERE", "placeholder_key", ""]:
        gemini_status = "configured"
        
    reports_status = "ready"
    if not os.path.exists("./static/reports"):
        reports_status = "directory_missing"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "gemini_api": gemini_status,
        "reports_exporter": reports_status,
        "app_env": settings.APP_ENV
    }

@router.get("/metrics")
def metrics():
    """Exposes system metrics including CPU, Memory, and DB performance parameters."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    # Calculate simple latency of a database check
    t_start = time.time()
    supabase = get_supabase_unauth()
    check_db_health(supabase)
    db_latency_ms = int((time.time() - t_start) * 1000)

    return {
        "process_id": os.getpid(),
        "cpu_usage_percent": psutil.cpu_percent(),
        "memory_used_mb": round(memory_info.rss / (1024 * 1024), 2),
        "db_query_latency_ms": db_latency_ms
    }

@router.get("/system/info")
def system_info():
    """Returns static and dynamic application details, including version and uptime."""
    uptime_seconds = int(time.time() - START_TIME)
    
    # Format uptime nicely
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

    return {
        "app_name": "AquaSentinel-AI Agentic Platform",
        "app_version": "1.0.0-rc1",
        "uptime_seconds": uptime_seconds,
        "uptime_formatted": uptime_str,
        "langgraph_status": "compiled",
        "vision_provider_status": "ready"
    }
