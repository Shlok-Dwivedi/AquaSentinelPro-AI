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
                                  ├─► [Water Scoring Engine] (Deterministic Python calculations)
                                  ├─► [Water Analysis Agent] (Gemini explanation)
                                  ├─► [Knowledge Agent] (Cross-validates against WHO/BIS specifications)
                                  ├─► [Reflection Agent] (logical consistency checks)
                                  └─► [Synthesizer] (Markdown formatting)
```

---

## 2. Stateful Multi-Agent Design with LangGraph

Instead of loose conversational prompts, the platform orchestrates interactions through a stateful Directed Acyclic Graph (DAG) powered by **LangGraph**.

### Execution Lifecycle

1. **State Initialization**: The API controller injects user queries, chemical parameters, and image file references into `AgentState`.
2. **Context Retrieval**: The **Memory Agent** queries database records to append historical location, water source, and purifier models.
3. **Planning & Routing**: The **Planning Agent** uses semantic routing to generate a task list mapping required specialist agents and their dependency constraints.
4. **Scoring & Analysis**:
   * **Water Scoring Engine**: A deterministic, rule-based Python module calculates the quality score (0–100), drinking safety category, risk level, and penalty breakdown.
   * **Water Analysis Agent**: Receives parameters and the calculated score, and calls Gemini Flash to generate observations, scientific explanations, and possible contamination causes.
5. **Knowledge Agent Validation**:
   * Programmatically loads regulatory limits from external sheets (`WHO.json` and `BIS.json`).
   * Evaluates the chemical parameters against the acceptable ranges of both organizations and lists any deviations.
6. **Reflection Gate**:
   * The **Reflection Agent** compares the outputs of the Water Analysis and Knowledge Agents.
   * Checks for safety contradictions (e.g. is water marked safe while having severe limits deviations).
   * If logical inconsistencies are found, it sets `is_valid` to `False` and returns detailed refinement instructions, routing the workflow back to the Water Analysis node (Max iterations = 3).
7. **Synthesizer**: Compiles the validated agent logs into a clean, professional markdown report for the user.

---

## 3. Reference Standards Specifications

To avoid hardcoded standard thresholds inside prompt strings, the platform stores regulatory specifications in structured JSON databases under `backend/app/knowledge/`:
* **`WHO.json`**: pH 6.5–8.5, TDS < 500, Turbidity < 5, Chlorine < 5, Fluoride < 1.5, Hardness < 300.
* **`BIS.json`**: pH 6.5–8.5, TDS < 500 (permissible 2000), Turbidity < 1 (permissible 5), Hardness < 200 (permissible 600), Chlorine min 0.2 (residual), Fluoride < 1.0 (permissible 1.5).

This allows developers to extend or update reference guidelines without modifying any AI prompts.

---

## 4. Extended Relational Database Design

The schema is built to track sessions, historical tests, PDF documents, and agent trace outputs:

* **`users`**: General profiles and location tags.
* **`chat_sessions`** & **`chat_messages`**: Conversational history storage.
* **`agent_execution_logs`**: Holds detailed trace metrics including:
  * `water_score`: The calculated water quality score.
  * `confidence_score`: Average confidence score returned by the agent nodes.
  * `graph_version`: The software trace version identifier.
  * `gemini_model`: The model used (e.g. `gemini-2.5-flash`).
  * `reflection_iterations`: The number of loops required.
  * `agents_executed`: List of agents activated during the run.
  * `synthesized_response`: Copy of the final markdown report.
* **`water_analyses`**: Water chemical readings.
* **`complaints`**: Drafted complaint templates.
* **`reports`**: Path to compiled water safety reports.
