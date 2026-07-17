# 🚢 AquaSentinel-AI Deployment Guide

This document describes how to deploy the AquaSentinel-AI Agentic Platform in local development, testing, and production environments.

---

## 📋 Prerequisites
Ensure the following tools are installed on your machine:
* **Docker** & **Docker Compose**
* **Node.js** (v18 or higher)
* **Python** (3.11 or higher)

---

## 🐳 Containerized Production Deployment (Recommended)

To spin up the entire application stack (FastAPI Backend, React Frontend, Nginx Reverse Proxy, PostgreSQL Database) with a single command:

1. **Clone the Release Branch:**
   ```bash
   git checkout release/v1.0
   ```

2. **Configure Environment Settings:**
   Create a `.env` file in the root directory (refer to [backend/.env.example](file:///e:/Projects/AquaSentinel-AI-main/backend/.env.example) for reference):
   ```bash
   APP_ENV=production
   DATABASE_URL=postgresql://postgres:postgrespassword@db:5432/aquasentinel
   GEMINI_API_KEY=your_actual_gemini_api_key
   SECRET_KEY=generate_a_long_random_jwt_signing_key_here
   ```

3. **Build and Run Containers:**
   ```bash
   docker compose up -d --build
   ```

4. **Verify Application Availability:**
   * React Web Portal: [http://localhost](http://localhost)
   * FastAPI swagger docs: [http://localhost/docs](http://localhost/docs)
   * Backend health check: [http://localhost/health](http://localhost/health)

---

## 🛠️ Local Development Server Deployment

If you want to run the servers natively without Docker containers:

### 1. Python FastAPI Backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/macOS
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --port 8000 --reload
```

### 2. React Vite Frontend:
```bash
cd frontend
npm install
npm run dev
```
* Web interface is served at [http://localhost:5173](http://localhost:5173)
* API endpoint calls automatically redirect to port `8000` via Nginx or local Axios proxy.
