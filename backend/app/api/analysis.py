import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from app.services.db_service import get_db
from app.services.auth_service import get_current_user
from app.models.db_models import User, Report, AgentExecutionLog, ChatSession, ChatMessage

logger = logging.getLogger("aquasentinel")

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.get("/dashboard")
async def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves authenticated user dashboard statistics, analytics, and chronologically unified recent activities."""
    # 1. Fetch count stats
    total_reports = db.query(Report).filter(Report.user_id == current_user.id).count()
    
    # Query logs executed for this user (join chat messages and sessions to map to user_id)
    execution_logs_query = db.query(AgentExecutionLog).join(
        ChatMessage, AgentExecutionLog.chat_message_id == ChatMessage.id
    ).join(
        ChatSession, ChatMessage.session_id == ChatSession.id
    ).filter(
        ChatSession.user_id == current_user.id
    )
    
    total_analyses = execution_logs_query.filter(AgentExecutionLog.water_score != None).count()
    images_analyzed = execution_logs_query.filter(AgentExecutionLog.image_filename != None).count()
    
    # Average Water Quality Score
    avg_score_res = execution_logs_query.with_entities(
        func.avg(AgentExecutionLog.water_score)
    ).first()
    avg_score = round(avg_score_res[0], 1) if avg_score_res and avg_score_res[0] is not None else 100.0
    
    # 2. Previous analyses (mapped from trace logs)
    analyses_records = execution_logs_query.order_by(AgentExecutionLog.created_at.desc()).limit(10).all()
    previous_analyses = []
    for log in analyses_records:
        water_out = log.final_outputs_json.get("water_analysis", {}) if log.final_outputs_json else {}
        if water_out:
            previous_analyses.append({
                "log_id": log.id,
                "score": log.water_score or 100.0,
                "risk_level": water_out.get("risk_level", "Low"),
                "safety": water_out.get("drinking_safety", "Safe"),
                "contaminants": log.plan_json.get("selected_agents", []) if log.plan_json else [],
                "created_at": log.created_at.isoformat()
            })

    # 3. Previous reports list
    reports_records = db.query(Report).filter(Report.user_id == current_user.id).order_by(Report.created_at.desc()).limit(10).all()
    previous_reports = [
        {
            "id": r.id,
            "title": r.title,
            "summary": r.summary,
            "created_at": r.created_at.isoformat()
        } for r in reports_records
    ]

    # 4. Chat history (sessions list)
    sessions_records = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).limit(5).all()
    chat_history = [
        {
            "session_id": s.id,
            "created_at": s.created_at.isoformat()
        } for s in sessions_records
    ]

    # 5. Compiled Recent Activity Feed
    recent_activity = []
    # Merge reports created
    for r in reports_records[:5]:
        recent_activity.append({
            "type": "report",
            "message": f"Compiled report '{r.title}'",
            "timestamp": r.created_at.isoformat()
        })
    # Merge image analyses
    image_records = execution_logs_query.filter(AgentExecutionLog.image_filename != None).order_by(AgentExecutionLog.created_at.desc()).limit(5).all()
    for img in image_records:
        recent_activity.append({
            "type": "vision",
            "message": f"Analyzed uploaded image '{img.image_filename}' for contamination",
            "timestamp": img.created_at.isoformat()
        })
    # Merge parameters logs
    for log in analyses_records[:5]:
        recent_activity.append({
            "type": "analysis",
            "message": f"Evaluated chemical logs (Score: {log.water_score or 100})",
            "timestamp": log.created_at.isoformat()
        })
        
    # Sort unified activity chronologically descending
    recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)

    return {
        "stats": {
            "total_analyses": total_analyses,
            "reports_generated": total_reports,
            "images_analyzed": images_analyzed,
            "average_water_score": avg_score
        },
        "previous_analyses": previous_analyses,
        "previous_reports": previous_reports,
        "chat_history": chat_history,
        "recent_activity": recent_activity[:10]
    }
