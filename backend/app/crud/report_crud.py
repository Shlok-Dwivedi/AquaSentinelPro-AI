from supabase import Client
from typing import List, Optional

def get_execution_log(supabase: Client, log_id: str) -> Optional[dict]:
    resp = supabase.table("agent_execution_logs").select("*").eq("id", log_id).execute()
    return resp.data[0] if resp.data else None

def get_user_reports(supabase: Client, user_id: str) -> List[dict]:
    resp = supabase.table("reports").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return resp.data

def get_report_by_id(supabase: Client, report_id: str, user_id: str) -> Optional[dict]:
    resp = supabase.table("reports").select("*").eq("id", report_id).eq("user_id", user_id).execute()
    return resp.data[0] if resp.data else None

def delete_report(supabase: Client, report_id: str, user_id: str) -> bool:
    resp = supabase.table("reports").delete().eq("id", report_id).eq("user_id", user_id).execute()
    return bool(resp.data)

def insert_report(supabase: Client, report_data: dict) -> dict:
    resp = supabase.table("reports").insert(report_data).execute()
    if not resp.data:
        raise Exception("Failed to insert report")
    return resp.data[0]
