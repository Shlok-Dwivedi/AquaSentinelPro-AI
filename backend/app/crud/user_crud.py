from typing import Optional
from supabase import Client

def get_user_by_id(supabase: Client, user_id: str) -> Optional[dict]:
    resp = supabase.table("users").select("*").eq("id", user_id).execute()
    if resp.data:
        return resp.data[0]
    return None

def create_user(supabase: Client, user_data: dict) -> Optional[dict]:
    resp = supabase.table("users").insert(user_data).execute()
    if resp.data:
        return resp.data[0]
    return None

def get_or_create_user(supabase: Client, user_id: str) -> dict:
    user = get_user_by_id(supabase, user_id)
    if user:
        return user
        
    new_user = {
        "id": user_id,
        "name": "Default User",
        "location": "Mumbai, India",
        "water_source": "Municipal Tap",
        "household_size": 4,
        "memory_context": {
            "purifier_type": "None",
            "reported_alerts": []
        }
    }
    return create_user(supabase, new_user) or new_user

def load_user_memory_context(supabase: Client, user_id: str) -> dict:
    user = get_or_create_user(supabase, user_id)
    
    # Query chat sessions to get messages, then get logs
    sessions_resp = supabase.table("chat_sessions").select("id").eq("user_id", user_id).execute()
    session_ids = [s["id"] for s in sessions_resp.data]
    
    logs_data = []
    if session_ids:
        msg_resp = supabase.table("chat_messages").select("id").in_("session_id", session_ids).execute()
        message_ids = [m["id"] for m in msg_resp.data]
        
        if message_ids:
            logs_resp = supabase.table("agent_execution_logs").select("*").in_("chat_message_id", message_ids).order("created_at", desc=True).execute()
            logs_data = logs_resp.data
            
    water_logs = [l for l in logs_data if l.get("water_score") is not None]
    
    analysis_count = len(water_logs)
    latest_score = water_logs[0]["water_score"] if analysis_count > 0 else None
    
    latest_risk = None
    if analysis_count > 0 and water_logs[0].get("final_outputs_json"):
        water_out = water_logs[0]["final_outputs_json"].get("water_analysis", {})
        latest_risk = water_out.get("risk_level")
    
    # Query complaints count
    complaints_resp = supabase.table("complaints").select("id", count="exact").eq("user_id", user_id).execute()
    complaint_count = complaints_resp.count if complaints_resp.count else 0
    
    return {
        "user_id": user["id"],
        "name": user["name"],
        "location": user["location"],
        "water_source": user["water_source"],
        "household_size": user["household_size"],
        "memory_context": user["memory_context"] or {},
        "history": {
            "total_analyses": analysis_count,
            "latest_water_score": latest_score,
            "latest_risk_level": latest_risk,
            "total_complaints": complaint_count
        }
    }
