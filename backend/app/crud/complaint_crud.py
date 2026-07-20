from supabase import Client
from typing import Dict, Any, List

def insert_complaint(supabase: Client, user_id: str, payload: dict) -> dict:
    new_complaint = {
        "user_id": user_id,
        "department": "Municipal Water and Sanitation Division",
        "severity": "Critical" if "discoloration" in str(payload).lower() or "foam" in str(payload).lower() else "Medium",
        "subject": payload.get("subject", "Urgent: Contaminated Drinking Water Supply in Area"),
        "body": payload.get("message", "Respected Sir/Madam,\n\nI am writing to report an issue with our tap water supply. Please look into this immediately.\n\nSincerely,\nResident"),
        "status": "Draft"
    }
    resp = supabase.table("complaints").insert(new_complaint).execute()
    if not resp.data:
        raise Exception("Failed to create complaint")
    return resp.data[0]

def get_user_complaints(supabase: Client, user_id: str) -> List[dict]:
    resp = supabase.table("complaints").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return resp.data

def submit_complaint_status(supabase: Client, complaint_id: str, user_id: str) -> bool:
    resp = supabase.table("complaints").select("id").eq("id", complaint_id).eq("user_id", user_id).execute()
    if not resp.data:
        return False
    
    supabase.table("complaints").update({"status": "Submitted"}).eq("id", complaint_id).execute()
    return True
