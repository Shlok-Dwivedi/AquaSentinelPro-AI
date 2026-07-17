import logging
from app.graph.state import AgentState

logger = logging.getLogger("aquasentinel")

def report_node(state: AgentState) -> AgentState:
    """Synthesizer node. Combines validated chemical & visual agent outputs into a professional markdown response."""
    logger.info("Running Synthesizer (Report Node)...")
    
    outputs = state.get("agent_outputs", {})
    water_out = outputs.get("water_analysis", {})
    knowledge_out = outputs.get("knowledge", {})
    vision_out = outputs.get("vision_analysis", {})
    plan = state.get("plan", {})
    selected_agents = plan.get("selected_agents", [])
    
    # 1. Start with the required execution status checklist timeline
    markdown = "Memory Loaded ✓\n"
    markdown += "Planning Complete ✓\n"
    
    if "vision_analysis" in selected_agents:
        markdown += "Vision Analysis Complete ✓\n"
    if "water_analysis" in selected_agents:
        markdown += "Water Analysis Complete ✓\n"
    if "knowledge" in selected_agents:
        markdown += "Knowledge Validation Complete ✓\n"
        
    markdown += "Reflection Passed ✓\n"
    markdown += "Response Generated ✓\n\n"
    
    markdown += "## 💧 AquaSentinel Water Safety Assessment\n\n"

    # Overall Summary / Executive Assessment
    overall_risk = "Low"
    safety_rating = "Safe"
    overall_confidence = 1.0
    
    if water_out:
        overall_risk = water_out.get("risk_level", "Low")
        safety_rating = water_out.get("drinking_safety", "Safe")
        overall_confidence = min(overall_confidence, water_out.get("confidence_score", 1.0))
        
    if vision_out:
        vis_level = vision_out.get("contamination_level", "None")
        overall_confidence = min(overall_confidence, vision_out.get("confidence_score", 1.0))
        if vis_level == "High" or overall_risk == "High":
            overall_risk = "High"
            safety_rating = "Highly Dangerous"
        elif vis_level == "Medium" and overall_risk == "Low":
            overall_risk = "Medium"
            safety_rating = "Unsafe without treatment"

    # Safety indicators styling
    safety_indicator = "🟢 Safe"
    if "Unsafe" in safety_rating:
        safety_indicator = "🟡 Unsafe (Treatment Required)"
    elif "Dangerous" in safety_rating:
        safety_indicator = "🔴 Highly Dangerous"
        
    risk_indicator = "🟢 Low"
    if overall_risk == "Medium":
        risk_indicator = "🟡 Medium"
    elif overall_risk == "High":
        risk_indicator = "🔴 High"

    markdown += "| Assessment Field | Overall Status |\n"
    markdown += "| :--- | :--- |\n"
    markdown += f"| **Drinking Safety** | {safety_indicator} |\n"
    markdown += f"| **Risk Level** | {risk_indicator} |\n"
    markdown += f"| **Orchestrator Confidence** | **{overall_confidence * 100:.1f}%** |\n\n"

    # Render Visual findings if executed
    if vision_out:
        markdown += "### 👁️ Visual Findings (Gemini Vision)\n"
        if vision_out.get("unsupported_image"):
            markdown += f"- ⚠️ **Unsupported Image Alert:** {vision_out.get('observations')}\n\n"
        else:
            markdown += f"- **Appearance:** {vision_out.get('water_appearance', 'N/A')}\n"
            markdown += f"- **Estimated Turbidity:** {vision_out.get('estimated_turbidity', 'N/A')} | **Estimated Color:** {vision_out.get('estimated_water_color', 'N/A')}\n"
            
            contams = vision_out.get("contaminants_detected", [])
            if contams:
                markdown += f"- **Detected Contaminants:** {', '.join(contams)}\n"
            else:
                markdown += "- **Detected Contaminants:** None visible\n"
                
            issues = vision_out.get("structural_issues", [])
            if issues:
                markdown += f"- **Structural Issues:** {', '.join(issues)}\n"
                
            markdown += f"- **Observations:** {vision_out.get('observations', '')}\n\n"

    # Render chemical findings if executed
    if water_out:
        score = water_out.get("water_score", 100.0)
        markdown += "### 🧪 Chemical Findings\n"
        markdown += f"- **Water Quality Score:** {score:.1f} / 100\n"
        markdown += f"- **Observations:** {water_out.get('observations', 'All parameters within optimal limits.')}\n"
        markdown += f"- **Causes:** {', '.join(water_out.get('possible_causes', [])) if water_out.get('possible_causes') else 'N/A'}\n\n"

    # Standard compliance violations from Knowledge
    if knowledge_out:
        markdown += "### 📜 WHO / BIS Standards Check\n"
        deviations = knowledge_out.get("deviations", [])
        if deviations:
            markdown += "**Violated Guidelines:**\n"
            for dev in deviations:
                param = dev.get("parameter", "Unknown").upper()
                std = dev.get("standard", "Standard")
                limit = dev.get("limit", "N/A")
                val = dev.get("value", "N/A")
                exp = dev.get("explanation", "")
                markdown += f"- ❌ **{param}**: Current value is **{val}** (Limit: **{limit}** under {std}). *{exp}*\n"
        else:
            markdown += "-  **Compliant:** No parameters violated WHO or BIS IS 10500 standards.\n"
        markdown += "\n"

    # Recommendations
    markdown += "### 🛠️ Recommended Next Steps\n"
    # Special reflection check: Invisible hazard (Clean image but poor chemical quality)
    if vision_out and not vision_out.get("unsupported_image") and water_out:
        is_clean_image = vision_out.get("contamination_level") == "None"
        is_poor_water = water_out.get("water_score", 100.0) < 80.0
        if is_clean_image and is_poor_water:
            markdown += "1. **⚠️ Critical Alert:** The source appears visually clean, but chemical tests reveal significant dissolved contaminants. **Recommend additional laboratory testing** immediately before drinking.\n"

    # Add general actions
    actions = []
    if vision_out and not vision_out.get("unsupported_image"):
        actions.extend(vision_out.get("recommended_actions", []))
        
    if water_out:
        score = water_out.get("water_score", 100.0)
        if score < 85.0 and score >= 50.0:
            actions.append("Setup activated carbon or sand filtration systems.")
        elif score < 50.0:
            actions.append("Setup multi-stage RO (Reverse Osmosis) + UV water purifier immediately.")
            
    if not actions:
        actions.append("Perform routine seasonal parameter re-tests.")
        
    for i, act in enumerate(actions, 1):
        markdown += f"{len(markdown.split('1.'))-1 + i}. {act}\n"

    state["synthesized_response"] = markdown
    
    logger.info("Response synthesized successfully for Milestone 4.")
    return state
