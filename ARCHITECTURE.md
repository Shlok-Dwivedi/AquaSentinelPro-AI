# Architecture Documentation: AquaSentinel-AI Agentic Platform

AquaSentinel-AI is a production-grade multi-agent AI system designed to solve complex citizen water safety, purification, and reporting requests under **UN SDG 6 (Clean Water and Sanitation)**.

---

## 1. System Topology

```
                  ┌───────────────────────────────┐
                  │      React Web Dashboard      │
                  └───────────────┬───────────────┘
                                  │
                       HTTP REST  │  File Uploads
                                  ▼
                  ┌───────────────────────────────┐
                  │        FastAPI Gateway        │
                  └───────────────┬───────────────┘
                                  │
                         Trigger  │  Query / Save
                                  ▼
                  ┌───────────────────────────────┐
                  │    LangGraph State Machine    │
                  └───────────────┬───────────────┘
                                  │
                                  ├─► [Memory Agent]
                                  ├─► [Planning Agent]
                                  ├─► [Specialist Agents]
                                  │     ├─ Water Analyst
                                  │     ├─ Vision Analyst
                                  │     ├─ Compliance Validator
                                  │     ├─ Purification Advisor
                                  │     ├─ Conservation Planner
                                  │     └─ Complaint Drafter
                                  ├─► [Reflection Agent]
                                  └─► [Report PDF compiler]
```

---

## 2. Stateful Multi-Agent Design with LangGraph

Instead of loose conversational prompts, the platform orchestrates interactions through a stateful Directed Acyclic Graph (DAG) powered by **LangGraph**. 

### Execution Lifecycle

1. **State Initialization**: The API controller injects user queries, chemical parameters, and image file references into `AgentState`.
2. **Context Retrieval**: The **Memory Agent** queries database records to append historical location, water source, and purifier models.
3. **Planning & Routing**: The **Planning Agent** uses semantic routing to generate a task list mapping required specialist agents and their dependency constraints.
4. **Execution Parallelism**:
   * *Water Analysis Agent* validates chemical thresholds.
   * *Vision Analysis Agent* analyzes visual items via Gemini Vision.
   * *Policy & Standards Agent* matches inputs to WHO/BIS limit databases.
   * *Purification & Conservation Agents* generate filtration selections and daily consumption saving recommendations.
5. **Quality Gate (Reflection)**: The **Reflection Agent** evaluates outputs. If the purification path fails to address identified policy deviations, a feedback payload is injected, and the graph reroutes back to the planning and specialist nodes for correction.
6. **Report compilation**: The **Report Generator Agent** compiles findings, triggers the PDF build engine, and routes outputs to the user.

---

## 3. Structured Data Communication

Agents communicate via structured JSON representations governed by Pydantic models. This guarantees data consistency and facilitates easy UI widget parsing.

For detail on JSON properties and schemas, see the implementation plan: [implementation_plan.md](file:///C:/Users/Shlok/.gemini/antigravity/brain/a7820cd7-45e8-474a-a6c4-63ed2482cba9/implementation_plan.md).

---

## 4. Relational Database Design

The schema is built to track sessions, historical tests, PDF documents, and agent trace outputs:

* **`users`**: General profiles and location tags.
* **`chat_sessions`** & **`chat_messages`**: Conversational history storage.
* **`agent_execution_logs`**: Holds planning lists, loop counts, reflection feedback, and final JSON dumps to audit agent reasoning steps.
* **`water_analyses`**: Water chemical readings.
* **`complaints`**: Drafted complaint templates.
* **`reports`**: Path to compiled water safety reports.
