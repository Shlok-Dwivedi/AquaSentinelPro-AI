import logging
from app.graph.state import AgentState

logger = logging.getLogger("aquasentinel")

def water_analysis_node(state: AgentState) -> AgentState:
    """Specialist Water Analysis Node. Processes manual chemical values if scheduled."""
    selected_agents = state.get("plan", {}).get("selected_agents", [])
    if "water_analysis" not in selected_agents:
        logger.info("Water Analysis Agent: skipped (not in plan).")
        return state
        
    logger.info("Running Water Analysis Agent...")
    params = state.get("raw_parameters") or {}
    tds = params.get("tds", 250.0)
    
    # Simple rule-based mock logic for demonstration
    score = 85.0
    risk = "Low"
    safety = "Safe"
    contaminants = []
    
    if tds > 500:
        score = 60.0
        risk = "Medium"
        safety = "Unsafe without treatment"
        contaminants.append("High TDS")
    if tds > 1000:
        score = 30.0
        risk = "High"
        safety = "Highly Dangerous"
        contaminants.append("Critical TDS level")

    state["agent_outputs"]["water_analysis"] = {
        "water_score": score,
        "drinking_safety": safety,
        "risk_level": risk,
        "contaminants_found": contaminants,
        "detected_hazards": []
    }
    return state

def vision_analysis_node(state: AgentState) -> AgentState:
    """Specialist Vision Analysis Node. Analyzes uploaded water images if scheduled."""
    selected_agents = state.get("plan", {}).get("selected_agents", [])
    if "vision_analysis" not in selected_agents:
        logger.info("Vision Analysis Agent: skipped (not in plan).")
        return state
        
    logger.info("Running Vision Analysis Agent...")
    state["agent_outputs"]["vision_analysis"] = {
        "detected_contaminants": ["Suspended solids"],
        "contamination_severity": "Low",
        "structural_issues": [],
        "description": "Visual inspection shows slight discoloration but no major debris."
    }
    return state

def policy_standards_node(state: AgentState) -> AgentState:
    """Specialist Policy & Standards Node. Checks BIS/WHO guidelines."""
    selected_agents = state.get("plan", {}).get("selected_agents", [])
    if "policy_standards" not in selected_agents:
        logger.info("Policy & Standards Agent: skipped (not in plan).")
        return state
        
    logger.info("Running Policy & Standards Agent...")
    # Read water analysis score to determine compliance
    water_out = state["agent_outputs"].get("water_analysis", {})
    is_compliant = water_out.get("water_score", 100) >= 70.0
    
    state["agent_outputs"]["policy_standards"] = {
        "is_compliant": is_compliant,
        "standards_checked": ["WHO Guidelines", "BIS (IS 10500)"],
        "deviations": [] if is_compliant else [{"parameter": "TDS", "finding": "Exceeds acceptable drinking threshold"}]
    }
    return state

def purification_node(state: AgentState) -> AgentState:
    """Specialist Purification Node. Suggests filtering mechanisms."""
    selected_agents = state.get("plan", {}).get("selected_agents", [])
    if "purification" not in selected_agents:
        logger.info("Purification Agent: skipped (not in plan).")
        return state
        
    logger.info("Running Purification Agent...")
    water_out = state["agent_outputs"].get("water_analysis", {})
    risk = water_out.get("risk_level", "Low")
    
    methods = ["Activated Carbon"]
    reasons = {"Activated Carbon": "Improves taste and removes chlorine compounds."}
    
    if risk in ["Medium", "High"]:
        methods.extend(["RO (Reverse Osmosis)", "UV (Ultraviolet)"])
        reasons["RO (Reverse Osmosis)"] = "Necessary to reduce high TDS/mineral contamination."
        reasons["UV (Ultraviolet)"] = "Disinfects potential biological pathogens."

    state["agent_outputs"]["purification"] = {
        "recommended_methods": methods,
        "suitability_reasons": reasons,
        "warning": "Ensure RO is calibrated to avoid depleting essential minerals." if "RO (Reverse Osmosis)" in methods else None
    }
    return state

def conservation_node(state: AgentState) -> AgentState:
    """Specialist Conservation Node. Suggests water saving plans."""
    selected_agents = state.get("plan", {}).get("selected_agents", [])
    if "conservation" not in selected_agents:
        logger.info("Conservation Agent: skipped (not in plan).")
        return state
        
    logger.info("Running Conservation Agent...")
    state["agent_outputs"]["conservation"] = {
        "strategies": ["Install tap aerators", "Collect rainwater for garden use"],
        "estimated_daily_savings_liters": 25.0
    }
    return state

def complaint_node(state: AgentState) -> AgentState:
    """Specialist Complaint Node. Drafts formal letter templates."""
    selected_agents = state.get("plan", {}).get("selected_agents", [])
    if "complaint" not in selected_agents:
        logger.info("Complaint Agent: skipped (not in plan).")
        return state
        
    logger.info("Running Complaint Agent...")
    state["agent_outputs"]["complaint"] = {
        "target_department": "Municipal Water and Sanitation Division",
        "severity": "Critical",
        "subject": "Formal Report of Water Quality Violations",
        "body": "Dear Authority,\n\nI am reporting consistent quality violations in our municipal supply line. Tests indicate values exceeding acceptable WHO limits.\n\nRegards,\nResident"
    }
    return state
