from supabase import Client

def check_db_health(supabase: Client) -> bool:
    try:
        supabase.table("users").select("id").limit(1).execute()
        return True
    except:
        return False
