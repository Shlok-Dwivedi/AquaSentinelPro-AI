import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from supabase import Client
from app.services.db_service import get_supabase
from app.services.auth_service import get_current_user
from app.crud.analysis_crud import get_dashboard_stats

logger = logging.getLogger("aquasentinel")

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.get("/dashboard")
async def get_user_dashboard(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Retrieves authenticated user dashboard statistics, analytics, and chronologically unified recent activities."""
    user_id = current_user["id"]
    
    # 1. Fetch count stats
    data = get_dashboard_stats(supabase, user_id)
    total_reports = data["total_reports"]
    sessions_data = data["sessions_data"]
    logs_data = data["logs_data"]
    reports_records = data["reports_records"]
        
    total_analyses = len(logs_data)
    images_analyzed = len([l for l in logs_data if l.get("image_filename") is not None])
    
    # Average Water Quality Score
    scores = []
    for log in logs_data:
        score = log.get("water_score")
        if score is None:
            vision_out = log.get("final_outputs_json", {}).get("vision_analysis", {}) if log.get("final_outputs_json") else {}
            if vision_out and vision_out.get("contamination_level") == "High":
                score = 20.0
            elif vision_out and vision_out.get("contamination_level") == "Medium":
                score = 60.0
            elif vision_out:
                score = 100.0
        if score is not None:
            scores.append(score)
            
    avg_score = round(sum(scores) / len(scores), 1) if scores else 100.0
    
    # 2. Previous analyses (mapped from trace logs)
    previous_analyses = []
    for log in logs_data[:10]:
        water_out = log.get("final_outputs_json", {}).get("water_analysis", {}) if log.get("final_outputs_json") else {}
        vision_out = log.get("final_outputs_json", {}).get("vision_analysis", {}) if log.get("final_outputs_json") else {}
        
        score = log.get("water_score")
        if score is None:
            if vision_out and vision_out.get("contamination_level") == "High":
                score = 20.0
            elif vision_out and vision_out.get("contamination_level") == "Medium":
                score = 60.0
            else:
                score = 100.0
                
        safety = water_out.get("drinking_safety")
        if not safety and vision_out:
             safety = "Dangerous" if vision_out.get("contamination_level") == "High" else "Safe"
             
        risk = water_out.get("risk_level")
        if not risk and vision_out:
             risk = vision_out.get("contamination_level")

        previous_analyses.append({
            "log_id": log["id"],
            "score": score,
            "risk_level": risk or "Low",
            "safety": safety or "Safe",
            "contaminants": log.get("plan_json", {}).get("selected_agents", []) if log.get("plan_json") else [],
            "created_at": log["created_at"]
        })

    # 3. Previous reports list
    previous_reports = [
        {
            "id": r["id"],
            "title": r["title"],
            "summary": r["summary"],
            "created_at": r["created_at"]
        } for r in reports_records
    ]

    # 4. Chat history (sessions list)
    chat_history = [
        {
            "session_id": s["id"],
            "created_at": s["created_at"]
        } for s in sorted(sessions_data, key=lambda x: x["created_at"], reverse=True)[:5]
    ]

    # 5. Compiled Recent Activity Feed
    recent_activity = []
    # Merge reports created
    for r in reports_records[:5]:
        recent_activity.append({
            "type": "report",
            "message": f"Compiled report '{r['title']}'",
            "timestamp": r["created_at"]
        })
        
    for log in logs_data[:5]:
        if log.get("image_filename"):
            recent_activity.append({
                "type": "vision",
                "message": f"Analyzed uploaded image '{log['image_filename']}'",
                "timestamp": log["created_at"]
            })
        elif log.get("water_score") is not None:
            recent_activity.append({
                "type": "analysis",
                "message": f"Evaluated chemical logs (Score: {log['water_score']})",
                "timestamp": log["created_at"]
            })
        else:
            recent_activity.append({
                "type": "analysis",
                "message": "Executed AI pipeline assessment",
                "timestamp": log["created_at"]
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
