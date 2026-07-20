import os
import requests
from dotenv import load_dotenv

load_dotenv('../frontend/.env')
url = os.getenv('VITE_SUPABASE_URL')
key = os.getenv('VITE_SUPABASE_ANON_KEY')

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

tables = ["users", "chat_sessions", "chat_messages", "water_analyses", "complaints", "reports", "agent_execution_logs"]
for t in tables:
    resp = requests.get(f"{url}/rest/v1/{t}?limit=1", headers=headers)
    print(f"Table {t}: {resp.status_code}")
