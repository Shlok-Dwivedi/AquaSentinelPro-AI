from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    # Inputs
    user_id: str
    session_id: str
    user_query: str
    raw_parameters: Optional[Dict[str, float]]
    image_path: Optional[str]
    
    # Context
    user_memory: Dict[str, Any]
    
    # Orchestration & Routing
    plan: List[Dict[str, Any]]
    current_step: int
    iterations: int
    
    # Inter-agent Structured Data Store
    agent_outputs: Dict[str, Any]
    reflection_feedback: Optional[str]
    is_valid: bool
    
    # Final Output
    synthesized_response: str
    pdf_report_url: Optional[str]
