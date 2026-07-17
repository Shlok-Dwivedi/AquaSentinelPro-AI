import logging
from app.graph.state import AgentState
from app.agents.water_analyst import run_water_analyst
from app.agents.knowledge import run_knowledge_agent

logger = logging.getLogger("aquasentinel")

def water_analysis_node(state: AgentState) -> AgentState:
    """Specialist Water Analysis Node. Calls scoring engine and prompts Gemini for reasoning."""
    selected_agents = state.get("plan", {}).get("selected_agents", [])
    if "water_analysis" not in selected_agents:
        logger.info("Water Analysis Agent: skipped (not in plan).")
        return state
        
    logger.info("Running Water Analysis Agent...")
    params = state.get("raw_parameters") or {}
    
    # Run the analyst agent
    result = run_water_analyst(params)
    
    # Store output in state matching schema dict
    state["agent_outputs"]["water_analysis"] = result.dict()
    logger.info(f"Water Analysis Agent finished. Score: {result.water_score}")
    return state

def knowledge_node(state: AgentState) -> AgentState:
    """Specialist Knowledge Node. Renamed from policy_standards_node. Validates limits against loaded WHO/BIS files."""
    selected_agents = state.get("plan", {}).get("selected_agents", [])
    if "knowledge" not in selected_agents:
        logger.info("Knowledge Agent: skipped (not in plan).")
        return state
        
    logger.info("Running Knowledge Agent...")
    params = state.get("raw_parameters") or {}
    
    # Run the knowledge agent
    result = run_knowledge_agent(params)
    
    state["agent_outputs"]["knowledge"] = result.dict()
    logger.info(f"Knowledge Agent finished. Compliant: {result.is_compliant}")
    return state

# Stubs for other agents kept for future milestones compatibility
def vision_analysis_node(state: AgentState) -> AgentState:
    selected_agents = state.get("plan", {}).get("selected_agents", [])
    if "vision_analysis" not in selected_agents:
        return state
    logger.info("Running Vision Analysis Agent (Stub)...")
    state["agent_outputs"]["vision_analysis"] = {
        "detected_contaminants": [],
        "contamination_severity": "None",
        "structural_issues": [],
        "description": "Visual stub execution."
    }
    return state

def purification_node(state: AgentState) -> AgentState:
    selected_agents = state.get("plan", {}).get("selected_agents", [])
    if "purification" not in selected_agents:
        return state
    logger.info("Running Purification Agent (Stub)...")
    state["agent_outputs"]["purification"] = {
        "recommended_methods": ["Activated Carbon"],
        "suitability_reasons": {"Activated Carbon": "Taste filter"},
        "warning": None
    }
    return state

def conservation_node(state: AgentState) -> AgentState:
    selected_agents = state.get("plan", {}).get("selected_agents", [])
    if "conservation" not in selected_agents:
        return state
    logger.info("Running Conservation Agent (Stub)...")
    state["agent_outputs"]["conservation"] = {
        "strategies": ["Conservation stub"],
        "estimated_daily_savings_liters": 0.0
    }
    return state

def complaint_node(state: AgentState) -> AgentState:
    selected_agents = state.get("plan", {}).get("selected_agents", [])
    if "complaint" not in selected_agents:
        return state
    logger.info("Running Complaint Agent (Stub)...")
    state["agent_outputs"]["complaint"] = {
        "target_department": "Municipal Board",
        "severity": "Low",
        "subject": "Stub Complaint",
        "body": "Mock draft details"
    }
    return state
