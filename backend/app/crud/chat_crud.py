from supabase import Client

def get_or_create_chat_session(supabase: Client, session_id: str | None, user_id: str) -> str:
    if not session_id:
        resp = supabase.table("chat_sessions").insert({"user_id": user_id}).execute()
        if not resp.data:
            raise Exception("Failed to create chat session")
        return resp.data[0]["id"]
    
    resp = supabase.table("chat_sessions").select("id").eq("id", session_id).execute()
    if not resp.data:
        resp = supabase.table("chat_sessions").insert({"id": session_id, "user_id": user_id}).execute()
        if not resp.data:
            raise Exception("Failed to create chat session")
        return resp.data[0]["id"]
    return resp.data[0]["id"]

def insert_chat_message(supabase: Client, session_id: str, role: str, content: str, image_path: str = None) -> str:
    msg_record = {
        "session_id": session_id,
        "role": role,
        "content": content or " ", # Ensure content is never empty (SQL schema NOT NULL)
        "image_path": image_path
    }
    resp = supabase.table("chat_messages").insert(msg_record).execute()
    if not resp.data:
        raise Exception("Failed to insert chat message")
    return resp.data[0]["id"]

def get_chat_history(supabase: Client, session_id: str) -> list:
    resp = supabase.table("chat_messages").select("*").eq("session_id", session_id).order("timestamp", desc=False).execute()
    return resp.data
