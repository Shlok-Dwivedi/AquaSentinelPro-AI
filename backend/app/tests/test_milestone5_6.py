import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add parent directories to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.main import app
from app.services.db_service import get_db, init_db
from app.models.db_models import User, Report
from app.services.auth_service import hash_password

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    """Initializes clean database schema for unit tests."""
    from app.services.db_service import engine
    from app.models.db_models import Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_auth_registration_and_login():
    """Verifies register, login, profile fetch, and logout flows."""
    email = "test_sprint@aquasentinel.org"
    password = "secure_password_123"
    
    # 1. Register User
    reg_res = client.post("/api/v1/auth/register", json={
        "name": "Sprint Engineer",
        "email": email,
        "password": password
    })
    assert reg_res.status_code == 200, reg_res.text
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    token = reg_data["access_token"]
    
    # 2. Get Profile info
    profile_res = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert profile_res.status_code == 200
    profile = profile_res.json()
    assert profile["email"] == email
    
    # 3. Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    
    # 4. Logout
    logout_res = client.post("/api/v1/auth/logout", headers={
        "Authorization": f"Bearer {token}"
    })
    assert logout_res.status_code == 200

def test_dashboard_and_reports():
    """Verifies dashboard analytics retrieval and report compilation."""
    email = "dash_test@aquasentinel.org"
    password = "secure_password_123"
    
    # Register & Auth
    reg_res = client.post("/api/v1/auth/register", json={
        "name": "Dashboard Tester",
        "email": email,
        "password": password
    })
    token = reg_res.json()["access_token"]
    
    # Fetch Dashboard stats
    dash_res = client.get("/api/v1/analysis/dashboard", headers={
        "Authorization": f"Bearer {token}"
    })
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert "stats" in dash_data
    assert dash_data["stats"]["total_analyses"] == 0
    assert dash_data["stats"]["reports_generated"] == 0
    
    # Fetch Reports list
    rep_res = client.get("/api/v1/reports", headers={
        "Authorization": f"Bearer {token}"
    })
    assert rep_res.status_code == 200
    assert len(rep_res.json()) == 0
