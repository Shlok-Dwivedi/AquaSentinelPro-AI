import logging
from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.nodes.memory import memory_load_node
from app.graph.nodes.planning import planning_node
from app.graph.nodes.specialists import water_analysis_node, knowledge_node
from app.graph.nodes.reflection import reflection_node
from app.graph.nodes.report import report_node

logger = logging.getLogger("aquasentinel")

# Initialize LangGraph StateGraph with schema
workflow = StateGraph(AgentState)

# Add nodes to graph
workflow.add_node("memory_load", memory_load_node)
workflow.add_node("planning", planning_node)
workflow.add_node("water_analysis", water_analysis_node)
workflow.add_node("knowledge", knowledge_node)
workflow.add_node("reflection", reflection_node)
workflow.add_node("synthesizer", report_node)

# Set entry point
workflow.set_entry_point("memory_load")

# Linear steps before worker analysis
workflow.add_edge("memory_load", "planning")
workflow.add_edge("planning", "water_analysis")
workflow.add_edge("water_analysis", "knowledge")
workflow.add_edge("knowledge", "reflection")

# Conditional Router from Reflection
def route_reflection(state: AgentState) -> str:
    """Decides if the workflow needs to loop back to Water Analysis for refinement or proceed to Synthesizer."""
    is_valid = state.get("is_valid", True)
    iterations = state.get("iterations", 0)
    
    if is_valid or iterations >= 3:
        logger.info(f"Reflection loop completed. is_valid={is_valid}, iterations={iterations}. Route to Synthesizer.")
        return "synthesizer"
    else:
        logger.warning(f"Reflection loop failed. Iteration count={iterations}. Routing back to Water Analysis for correction.")
        return "water_analysis"

workflow.add_conditional_edges(
    "reflection",
    route_reflection,
    {
        "synthesizer": "synthesizer",
        "water_analysis": "water_analysis"
    }
)

workflow.add_edge("synthesizer", END)

# Compile LangGraph
app_workflow = workflow.compile()
logger.info("LangGraph workflow compiled successfully for Milestone 3.")
