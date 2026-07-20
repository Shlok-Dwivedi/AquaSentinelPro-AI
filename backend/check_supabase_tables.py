import os
import requests
from dotenv import load_dotenv

load_dotenv('../frontend/.env')
url = os.getenv('VITE_SUPABASE_URL')
key = os.getenv('VITE_SUPABASE_ANON_KEY')

if not url or not key:
    print("No frontend keys found.")
    exit(1)

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

response = requests.get(f"{url}/rest/v1/users", headers=headers)
if response.status_code == 200:
    print("Table 'users' exists!")
else:
    print(f"Failed to fetch 'users' table: {response.status_code} {response.text}")
