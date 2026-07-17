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
                           ├─► Specialist Agents (Water, Vision, Policy, Purification, Conservation, Complaint)
                           ├─► Reflection Agent (validates outputs against thresholds)
                           └─► Report Agent (compiles findings to PDF)
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
│   │   ├── agents/                # AI Agents Prompt logic
│   │   ├── models/                # DB Models & API Pydantic schemas
│   │   ├── services/              # PDF & DB services
│   │   └── api/                   # REST endpoint routers
│   ├── requirements.txt           # Python backend packages
│   └── .env.example               # Backend environment templates
│
├── frontend/                      # React Frontend (Vite)
│   ├── src/
│   │   ├── components/            # Shared UI widgets
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
3. Copy environment settings:
   ```bash
   copy .env.example .env
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```
   * Swagger Documentation is available at: `http://localhost:8000/docs`
   * Health endpoint is available at: `http://localhost:8000/health`

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
