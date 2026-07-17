from langgraph.graph import StateGraph, END
from app.graph.state import AgentState

# Define empty placeholder node functions
def memory_load_node(state: AgentState) -> AgentState:
    # Pre-populate dummy memory structure if empty
    if not state.get("user_memory"):
        state["user_memory"] = {"location": "Unknown", "water_source": "Unknown", "history": []}
    return state

def planning_node(state: AgentState) -> AgentState:
    # Dummy plan
    state["plan"] = [{"agent": "water_analysis", "dependencies": []}]
    state["current_step"] = 0
    return state

def water_analysis_node(state: AgentState) -> AgentState:
    state["agent_outputs"]["water_analysis"] = {
        "water_score": 85.0,
        "drinking_safety": "Safe",
        "risk_level": "Low",
        "contaminants_found": [],
        "detected_hazards": []
    }
    return state

def vision_analysis_node(state: AgentState) -> AgentState:
    state["agent_outputs"]["vision_analysis"] = {
        "detected_contaminants": [],
        "contamination_severity": "None",
        "structural_issues": [],
        "description": "No visual contaminants detected."
    }
    return state

def policy_standards_node(state: AgentState) -> AgentState:
    state["agent_outputs"]["policy_standards"] = {
        "is_compliant": True,
        "standards_checked": ["WHO", "BIS"],
        "deviations": []
    }
    return state

def purification_node(state: AgentState) -> AgentState:
    state["agent_outputs"]["purification"] = {
        "recommended_methods": ["Activated Carbon"],
        "suitability_reasons": {"Activated Carbon": "Recommended for standard domestic tap water taste enhancement."},
        "warning": None
    }
    return state

def conservation_node(state: AgentState) -> AgentState:
    state["agent_outputs"]["conservation"] = {
        "strategies": ["Fix tap leaks", "Use aerators"],
        "estimated_daily_savings_liters": 15.0
    }
    return state

def complaint_node(state: AgentState) -> AgentState:
    state["agent_outputs"]["complaint"] = {
        "target_department": "Municipal Board",
        "severity": "Low",
        "subject": "General Water Query",
        "body": "This is a dummy complaint draft."
    }
    return state

def reflection_node(state: AgentState) -> AgentState:
    state["is_valid"] = True
    return state

def replanning_node(state: AgentState) -> AgentState:
    state["iterations"] += 1
    return state

def report_node(state: AgentState) -> AgentState:
    state["synthesized_response"] = "### AquaSentinel Safety Assessment Report\n\nWater quality is optimal. No action required."
    state["pdf_report_url"] = "/api/v1/reports/download/dummy-uuid"
    return state

def memory_sync_node(state: AgentState) -> AgentState:
    # Dummy sync log
    return state

# Build the LangGraph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("memory_load", memory_load_node)
workflow.add_node("planning", planning_node)
workflow.add_node("water_analysis", water_analysis_node)
workflow.add_node("vision_analysis", vision_analysis_node)
workflow.add_node("policy_standards", policy_standards_node)
workflow.add_node("purification", purification_node)
workflow.add_node("conservation", conservation_node)
workflow.add_node("complaint", complaint_node)
workflow.add_node("reflection", reflection_node)
workflow.add_node("replanning", replanning_node)
workflow.add_node("report_generation", report_node)
workflow.add_node("memory_sync", memory_sync_node)

# Define Transitions / Edges
workflow.set_entry_point("memory_load")

workflow.add_edge("memory_load", "planning")

# For the simple scaffold, run analysis agents sequentially and proceed
workflow.add_edge("planning", "water_analysis")
workflow.add_edge("water_analysis", "vision_analysis")
workflow.add_edge("vision_analysis", "policy_standards")
workflow.add_edge("policy_standards", "purification")
workflow.add_edge("purification", "conservation")
workflow.add_edge("conservation", "complaint")
workflow.add_edge("complaint", "reflection")

# Conditional Routing from Reflection
def route_reflection(state: AgentState) -> str:
    if state.get("is_valid", True) or state.get("iterations", 0) >= 3:
        return "report_generation"
    else:
        return "replanning"

workflow.add_conditional_edges(
    "reflection",
    route_reflection,
    {
        "report_generation": "report_generation",
        "replanning": "replanning"
    }
)

workflow.add_edge("replanning", "planning")
workflow.add_edge("report_generation", "memory_sync")
workflow.add_edge("memory_sync", END)

# Compile
app_workflow = workflow.compile()
