# 💧 AquaSentinelPro-AI Agentic Platform (UN SDG 6)

> **A Production-Grade, Stateful Multi-Agent AI System for Intelligent Water Safety Assessment, Visual Contaminant Detection, Regulatory Compliance Checking, and Professional Safety Report Generation.**

---

## 🌟 Project Overview

**AquaSentinelPro-AI** is a state-of-the-art agentic software system designed in alignment with **United Nations Sustainable Development Goal 6 (Clean Water and Sanitation)**. Developed as part of the **IBM SkillsBuild AI Internship**, the platform combines deep AI reasoning with deterministic verification algorithms to analyze tap water, rivers, and storage sources.

By orchestrating specialized AI agents, the platform interprets chemical properties (pH, TDS, Turbidity, Chlorine, etc.) and visual inputs (images) to compute safety ratings, cross-validate regulatory standards (WHO/BIS), and compile print-ready PDF reports.

---

## 🏗️ System Architecture & Workflow

AquaSentinelPro-AI uses **LangGraph** to construct a deterministic, stateful multi-agent execution DAG. This ensures logical consistency and logical verification gates:

```
                          ┌───────────────────────────┐
                          │    React Web Dashboard    │
                          └─────────────┬─────────────┘
                                        │  HTTP / Multipart Upload
                                        ▼
                          ┌───────────────────────────┐
                          │      FastAPI Gateway      │
                          └─────────────┬─────────────┘
                                        │  Graph Trigger
                                        ▼
                         ┌─────────────────────────────┐
                         │   LangGraph State Machine   │
                         └──────────────┬──────────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
     ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
     │ Memory Agent  │          │ Planner Agent │          │ Vision Agent  │
     │ (Session logs)│          │ (Task Router) │          │ (Gemini Vision│
     └───────────────┘          └───────┬───────┘          └───────────────┘
                                        │
             ┌──────────────────────────┴──────────────────────────┐
             ▼                                                     ▼
     ┌───────────────┐                                     ┌───────────────┐
     │ Water Analyst │                                     │  Knowledge    │
     │ (Scoring WQI) │                                     │  Validation   │
     └───────┬───────┘                                     │  (WHO / BIS)  │
             │                                             └───────┬───────┘
             └──────────────────────────┬──────────────────────────┘
                                        ▼
                               ┌─────────────────┐
                               │ Reflection Gate │◄─── [Loops back if inconsistent]
                               └────────┬────────┘
                                        ▼
                               ┌─────────────────┐
                               │   Synthesizer   │ ──► [Structured PDF Reports]
                               └─────────────────┘
```

---

## 🛠️ Technology Stack

| Category | Technology |
| :--- | :--- |
| **Backend Core** | FastAPI (Python 3.11/3.13), Uvicorn |
| **AI Orchestration** | LangGraph, LangChain, Google Generative AI (Gemini 2.5 Flash) |
| **Database & ORM** | PostgreSQL, SQLite, SQLAlchemy, Alembic Migrations |
| **PDF Generation** | ReportLab PDF Exporter |
| **Frontend Core** | React 19, Vite, Tailwind CSS v4, Lucide Icons |
| **Security** | PyJWT (JSON Web Tokens), Bcrypt Password Hashing |
| **Containerization** | Docker, Docker Compose, Nginx Reverse Proxy |
| **CI/CD** | GitHub Actions |

---

## 📁 Repository Structure

```
AquaSentinelPro-AI/
├── .github/workflows/      # CI Pipeline (flake8, pytest, build checks)
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI Gateway entrypoint
│   │   ├── config.py       # Pydantic Settings env loader
│   │   ├── graph/          # LangGraph definitions
│   │   ├── agents/         # AI Agent system prompts
│   │   ├── models/         # SQLAlchemy DB models & Pydantic schemas
│   │   ├── services/       # Exporters, auth, database services
│   │   ├── utils/          # Python WQI calculation engine
│   │   └── api/            # Route controllers (auth, chat, reports)
│   ├── requirements.txt    # Python backend packages
│   └── .env.example        # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/     # UI widgets (Sidebar)
│   │   └── pages/          # Pages (Dashboard, Chat, Report Hub, Login)
│   ├── nginx.conf          # Nginx reverse proxy configuration
│   └── Dockerfile          # Frontend compilation dockerfile
├── docker-compose.yml      # Containerized database & backend cluster
├── ARCHITECTURE.md         # Detailed systems design specifications
├── DEPLOYMENT.md           # Deployment manual (Render, Vercel, Postgres)
├── CONTRIBUTING.md         # Contribution guidelines
├── SECURITY.md             # Security policies & reporting channels
├── CHANGELOG.md            # Versions history log
└── README.md               # Home documentation page
```

---

## 🚀 Getting Started

### 1. Backend Setup (.env config)
Navigate to `/backend`, set up a virtual environment, and load variables:
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate    # Linux/macOS
pip install -r requirements.txt
copy .env.example .env      # Set actual keys or 'placeholder_key' for mock runs
alembic upgrade head
uvicorn app.main:app --port 8000 --reload
```
* **Swagger Interface:** `http://localhost:8000/docs`
* **Health endpoint:** `http://localhost:8000/health`

### 2. Frontend Setup
Navigate to `/frontend`, install packages, and boot the Vite compiler:
```bash
cd frontend
npm install
npm run dev
```
* Served locally at `http://localhost:5173`

### 3. Containerized Run (Docker Compose)
Build and run the entire stack (FastAPI, React, Nginx, Postgres):
```bash
docker compose up --build
```

---

## ☁️ Production Deployment Matrix

* **Backend Services:** Deploy on **Render** or **Railway** (Set `APP_ENV=production` and configure PostgreSQL DB string).
* **Frontend Services:** Deploy on **Vercel** or **Netlify** (Add rewrite rules mapping `/api` endpoints).
* **Database Volumes:** Deploy on **Render PostgreSQL** or AWS RDS instances.

For step-by-step instructions, see [DEPLOYMENT.md](file:///e:/Projects/AquaSentinel-AI-main/DEPLOYMENT.md).

---

## 📜 License & Author

Distributed under the **MIT License**. Created and maintained by **Shlok Dwivedi** for the **IBM SkillsBuild AI Internship**.
