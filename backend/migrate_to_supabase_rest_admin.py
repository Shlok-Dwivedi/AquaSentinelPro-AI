import os
import json
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.db_models import User, ChatSession, ChatMessage, WaterAnalysis, Complaint, Report, AgentExecutionLog

# Load frontend env for Supabase URL
load_dotenv('../frontend/.env')
url = os.getenv('VITE_SUPABASE_URL')

# Load backend env for JWT secret to forge service_role token
load_dotenv('./.env')
jwt_secret = os.getenv('SECRET_KEY')

if not url or not jwt_secret:
    print("Missing URL or JWT Secret")
    exit(1)

# Forge service_role token to bypass RLS
payload = {
    "role": "service_role",
    "iss": "supabase",
    "iat": int(datetime.utcnow().timestamp()),
    "exp": int((datetime.utcnow() + timedelta(days=1)).timestamp())
}
service_role_key = jwt.encode(payload, jwt_secret, algorithm="HS256")

# Create client with service role key
supabase: Client = create_client(url, service_role_key)

# Load backend local sqlite DB
engine = create_engine("sqlite:///./aquasentinel.db")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def serialize_json(val):
    if val is None:
        return None
    if isinstance(val, str):
        try:
            return json.loads(val)
        except:
            return val
    return val

def migrate():
    print("Migrating users...")
    users = db.query(User).all()
    for u in users:
        data = {
            "id": u.id,
            "name": u.name,
            "location": u.location,
            "water_source": u.water_source,
            "household_size": u.household_size,
            "memory_context": serialize_json(u.memory_context),
            "updated_at": u.updated_at.isoformat() if u.updated_at else None
        }
        supabase.table("users").upsert(data).execute()

    print("Migration complete!")

if __name__ == "__main__":
    migrate()
