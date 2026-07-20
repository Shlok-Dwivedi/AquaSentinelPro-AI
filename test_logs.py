import asyncio
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SECRET_KEY"))

res = supabase.table("agent_execution_logs").select("*").execute()
print(f"Total logs: {len(res.data)}")
if res.data:
    print(res.data[0])
