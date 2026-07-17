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

---

## 6. Report Exporter Pipeline

To deliver formal water safety assessments, the system uses a modular **Exporter Architecture** decoupled via the `ExportProvider` base interface:

```
                       ┌───────────────────────────────┐
                       │        ExportProvider         │  (Abstract Base Class)
                       └───────────────┬───────────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                ▼                      ▼                      ▼
   ┌────────────────────────┐  ┌───────────────┐  ┌────────────────────────┐
   │      PDFExporter       │  │ JSONExporter  │  │    MarkdownExporter    │
   │ (Styled ReportLab PDF) │  └───────────────┘  └────────────────────────┘
   └────────────────────────┘
```

* **PDFExporter**: Formats structural results, WHO standard violations, and visual findings into a clean, print-ready document using **ReportLab** elements.
* **MarkdownExporter**: Generates web-friendly summaries using standard Markdown layout.
* **JSONExporter**: Dumps raw structured data schemas for programmatic machine integrations.

On every successful analysis run (where water or vision agents execute), the `generate_water_report` agent executes these exporters concurrently, writes the compiled files into `static/reports/` directories, and registers a database `Report` log referencing the specific `AgentExecutionLog`.

---

## 7. Authentication & Session Security

To protect user dashboard analytics, the gateway implements standard JWT Bearer Token authentication controls:

* **Password Hashing**: User credentials are encrypted using native **bcrypt** password-hashing functions with a security workload scale of 12 rounds. Plaintext passwords are never stored.
* **JWT Access Tokens**: Stateless access signatures valid for 30 minutes.
* **Rotating Refresh Tokens**: Session durability is maintained using a rotating 7-day refresh token. To prevent session hijacking:
  * Refresh tokens are cryptographically hashed using SHA-256 before being stored in the database.
  * If a user tries to reuse a previous refresh token (token reuse anomaly), the entire session is immediately invalidated, revoking access.

---

## 8. System Diagnostics & Monitoring

The platform provides a diagnostic suite to ensure service reliability in high-throughput environments:

* **`/health`**: Checks API server status, database connectivity, and configuration variables (e.g. Gemini availability status).
* **`/metrics`**: Returns memory footprint (MB), CPU usage percentage, and active database connection query latency (ms) measured using `psutil`.
* **`/system/info`**: Exposes uptime duration, platform version metrics, and compiled graph flags.
* **Structured Rotating Logs**: Writes system audits as structured JSON objects to rotating files capped at 5MB, keeping 5 backup logs.

