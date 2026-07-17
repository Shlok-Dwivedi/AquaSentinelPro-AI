# Architecture Documentation: AquaSentinel-AI Agentic Platform

AquaSentinel-AI is a production-grade multi-agent AI system designed to solve complex citizen water safety, purification, and reporting requests under **UN SDG 6 (Clean Water and Sanitation)**.

---

## 1. System Topology

```
                  ┌───────────────────────────────┐
                  │      React Web Dashboard      │
                  └───────────────┬───────────────┘
                                  │
                       HTTP REST  │  File Uploads (Images)
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
                                  ├─► [Planning Agent] (Flags unsupported image uploads)
                                  ├─► [Vision Agent] (Analyzes visual algae, plastics, oil, foam)
                                  ├─► [Water Scoring Engine] (Deterministic Python calculations)
                                  ├─► [Water Analysis Agent] (Gemini explanation)
                                  ├─► [Knowledge Agent] (Cross-validates against WHO/BIS specifications)
                                  ├─► [Reflection Agent] (Audits visual and chemical contradictions)
                                  └─► [Synthesizer] (Markdown formatting)
```

---

## 2. Stateful Multi-Agent Design with LangGraph

Instead of loose conversational prompts, the platform orchestrates interactions through a stateful Directed Acyclic Graph (DAG) powered by **LangGraph**.

### Execution Lifecycle

1. **State Initialization**: The API controller injects user queries, chemical parameters, and image file references into `AgentState`.
2. **Context Retrieval**: The **Memory Agent** queries database records to append historical location, water source, and purifier models.
3. **Planning & Routing**:
   * The **Planning Agent** uses semantic routing to generate a task list mapping required specialist agents and their dependency constraints.
   * If an image is uploaded, it evaluates whether the file is related to water. If it is an unrelated image, it flags `is_water_image` as `False`, skips vision node processing, and sets an unsupported status trace.
4. **Vision Agent**:
   * Evaluates the image using the configured `VisionProvider` abstraction interface to extract physical contaminants (algae, plastics, oil, foam, silt) and structural issues.
5. **Scoring & Analysis**:
   * **Water Scoring Engine**: A deterministic, rule-based Python module calculates the quality score (0–100), drinking safety category, risk level, and penalty breakdown.
   * **Water Analysis Agent**: Receives parameters and the calculated score, and calls Gemini Flash to generate observations, scientific explanations, and possible contamination causes.
6. **Knowledge Agent Validation**:
   * Programmatically loads regulatory limits from external sheets (`WHO.json` and `BIS.json`).
   * Evaluates the chemical parameters against the acceptable ranges of both organizations and lists any deviations.
7. **Reflection Gate**:
   * The **Reflection Agent** compares the outputs of the Water Analysis, Knowledge, and Vision Agents.
   * Checks for safety contradictions (e.g. is water marked safe while having severe limits deviations).
   * Cross-checks visual contradictions (e.g. if the image contains severe green algae scum but the chemical water log registers turbidity as 0.0).
   * Flags invisible hazards: If the image appears completely clean, but chemical tests reveal severe contamination, it forces a special alert: *"The source appears visually clean, but chemical tests reveal significant dissolved contaminants. Recommend additional laboratory testing."*
   * If logical inconsistencies are found, it sets `is_valid` to `False` and returns detailed refinement instructions, routing the workflow back to the Water Analysis node (Max iterations = 3).
8. **Synthesizer**: Compiles the validated agent logs into a clean, professional markdown report for the user.

---

## 3. Vision Provider Abstraction

To ensure decoupling and local offline capability, we implement a provider-based pattern for image validation:

```
                  ┌───────────────────────────────┐
                  │        VisionProvider         │  (Abstract Base Class)
                  └───────────────┬───────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
    ┌─────────────────────────┐       ┌─────────────────────────┐
    │  GeminiVisionProvider   │       │   MockVisionProvider    │  (Offline testing)
    └─────────────────────────┘       └─────────────────────────┘
```

The system inspects the environment for `GEMINI_API_KEY`. If absent or marked as a placeholder, it automatically hooks `MockVisionProvider` into the Vision Agent. Predefined test images (e.g., `clean`, `murky`, `plastic`, `algae`, `oil`, `foam`, `unsupported`) resolve to deterministic visual data logs.

---

## 4. Reference Standards Specifications

To avoid hardcoded standard thresholds inside prompt strings, the platform stores regulatory specifications in structured JSON databases under `backend/app/knowledge/`:
* **`WHO.json`**: pH 6.5–8.5, TDS < 500, Turbidity < 5, Chlorine < 5, Fluoride < 1.5, Hardness < 300.
* **`BIS.json`**: pH 6.5–8.5, TDS < 500 (permissible 2000), Turbidity < 1 (permissible 5), Hardness < 200 (permissible 600), Chlorine min 0.2 (residual), Fluoride < 1.0 (permissible 1.5).

This allows developers to extend or update reference guidelines without modifying any AI prompts.

---

## 5. Extended Relational Database Design

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
  * `image_filename`, `image_width`, `image_height`, `mime_type`, `file_size`: Captured file details.
  * `vision_confidence`: Confidence score returned by the Vision provider.
  * `detected_hazards`: JSON list of contaminants observed in the image.
  * `contamination_level`: Contamination rating (None, Low, Medium, High).
* **`water_analyses`**: Water chemical readings.
* **`complaints`**: Drafted complaint templates.
* **`reports`**: Path to compiled water safety reports.
