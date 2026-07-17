import logging
from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.nodes.memory import memory_load_node
from app.graph.nodes.planning import planning_node
from app.graph.nodes.reflection import reflection_node
from app.graph.nodes.report import report_node

logger = logging.getLogger("aquasentinel")

# Initialize LangGraph StateGraph with schema
workflow = StateGraph(AgentState)

# Add nodes to graph
workflow.add_node("memory_load", memory_load_node)
workflow.add_node("planning", planning_node)
workflow.add_node("reflection", reflection_node)
workflow.add_node("report", report_node)

# Set entry point
workflow.set_entry_point("memory_load")

# Add linear edges for orchestration proof
workflow.add_edge("memory_load", "planning")
workflow.add_edge("planning", "reflection")
workflow.add_edge("reflection", "report")
workflow.add_edge("report", END)

# Compile LangGraph
app_workflow = workflow.compile()
logger.info("LangGraph workflow compiled successfully.")
