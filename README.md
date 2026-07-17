# 💧 AquaSentinel-AI Agentic Platform

> **An Agentic Multi-Agent System for Intelligent Water Safety, Purification Guidance, Water Conservation, and Automated Complaint Registration.**

This project is the official agentic AI implementation of AquaSentinel-AI for the **IBM SkillsBuild AI Internship**, focusing on **UN Sustainable Development Goal 6 (Clean Water and Sanitation)**.

---

## 🏗️ Architecture Summary

AquaSentinel-AI uses a stateful multi-agent system coordinated with **LangGraph** and **FastAPI** to process user queries, chemical readings, and images:

```
User Query / Form 
   │
   ▼
[FastAPI Backend] ──► [LangGraph Engine]
                           │
                           ├─► Memory Agent (fetches profile history)
                           ├─► Planning Agent (creates task list)
                           ├─► Water Scoring Engine (deterministic Python calculations)
                           ├─► Water Analysis Agent (Gemini reasoning on score)
                           ├─► Knowledge Agent (cross-validates against WHO/BIS specifications)
                           ├─► Reflection Agent (logical verification loop)
                           └─► Synthesizer (compiles findings into markdown)
```

For more detailed information, see [ARCHITECTURE.md](file:///e:/Projects/AquaSentinel-AI-main/ARCHITECTURE.md).

---

## 📁 Project Structure

```
AquaSentinel-AI/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI server entrypoint
│   │   ├── config.py              # Environment configuration loader
│   │   ├── graph/                 # LangGraph Workflow definitions
│   │   │   └── nodes/             # LangGraph state nodes (Memory, Planner, etc.)
│   │   ├── agents/                # AI Agents Prompt logic (Analyst, Reflector)
│   │   ├── knowledge/             # WHO and BIS specifications reference sheets
│   │   ├── models/                # DB Models & API Pydantic schemas
│   │   ├── services/              # Gemini & DB services
│   │   ├── utils/                 # Water scoring calculations engine
│   │   └── api/                   # REST endpoint routers
│   ├── requirements.txt           # Python backend packages
│   └── .env.example               # Backend environment templates
│
├── frontend/                      # React Frontend (Vite)
│   ├── src/
│   │   ├── components/            # Shared UI widgets (Sidebar)
│   │   └── pages/                 # Routing pages (Dashboard, Chat, etc.)
│   ├── package.json
│   └── tailwind.config.js
│
├── ARCHITECTURE.md                # Systems Architecture Specification
├── PROJECT_PROGRESS.md            # Work Tracker milestones list
└── README.md                      # General documentation
```

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* Node.js & NPM (or Anaconda)

### 1. Backend Setup
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Set up virtual environment and install packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment settings and configure database/Gemini key:
   ```bash
   copy .env.example .env
   ```
4. Run migrations:
   ```bash
   alembic upgrade head
   ```
5. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```
   * Swagger Documentation: `http://localhost:8000/docs`
   * Health endpoint: `http://localhost:8000/health`

### 2. Frontend Setup
1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install NPM packages:
   ```bash
   npm install
   ```
3. Start Vite dev server:
   ```bash
   npm run dev
   ```
4. Access dashboard in browser: `http://localhost:5173`

---

## 🧪 Running Automated Tests
The platform includes automated scenarios covering safe water, high TDS, unsafe pH, multiple contaminants, and incomplete parameters:
```bash
python backend/app/scratch/test_milestone3.py
```
