from supabase import Client

def get_dashboard_stats(supabase: Client, user_id: str):
    # 1. Fetch count stats
    reports_resp = supabase.table("reports").select("id", count="exact").eq("user_id", user_id).execute()
    total_reports = reports_resp.count if reports_resp.count else 0
    
    # A. Get sessions
    sessions_resp = supabase.table("chat_sessions").select("id, created_at").eq("user_id", user_id).execute()
    session_ids = [s["id"] for s in sessions_resp.data]
    
    # B. Get messages
    message_ids = []
    if session_ids:
        msg_resp = supabase.table("chat_messages").select("id").in_("session_id", session_ids).execute()
        message_ids = [m["id"] for m in msg_resp.data]
        
    # C. Get logs
    logs_data = []
    if message_ids:
        # Avoid passing empty list to in_ which might error in some clients, but message_ids is checked
        logs_resp = supabase.table("agent_execution_logs").select("*").in_("chat_message_id", message_ids).order("created_at", desc=True).execute()
        logs_data = logs_resp.data
        
    # D. Get reports
    reports_records = supabase.table("reports").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute().data
    
    return {
        "total_reports": total_reports,
        "sessions_data": sessions_resp.data,
        "logs_data": logs_data,
        "reports_records": reports_records
    }
