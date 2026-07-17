from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    # Inputs
    user_id: str
    session_id: str
    user_query: str
    image_path: Optional[str]                   # uploaded image path
    raw_parameters: Optional[Dict[str, float]]   # manual water parameters
    
    # Context & Memory
    user_memory: Dict[str, Any]                 # user memory
    
    # Orchestration & Routing
    plan: Dict[str, Any]                        # execution plan (selected_agents, dependencies, execution_order)
    current_step: int
    iterations: int                             # iteration count
    is_valid: bool
    
    # Inter-agent Structured Data Store
    agent_outputs: Dict[str, Any]               # agent outputs
    reflection_feedback: Optional[str]          # reflection feedback
    
    # Execution Diagnostic logs
    metadata: Dict[str, Any]                    # execution metadata (execution_time_ms, logs, status)
    
    # Final Output
    synthesized_response: str                   # final synthesized response
    pdf_report_url: Optional[str]
