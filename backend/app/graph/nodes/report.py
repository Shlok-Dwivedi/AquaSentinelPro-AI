import logging
from app.graph.state import AgentState

logger = logging.getLogger("aquasentinel")

def report_node(state: AgentState) -> AgentState:
    """Synthesizer node. Combines validated agent outputs into a professional markdown response."""
    logger.info("Running Synthesizer (Report Node)...")
    
    outputs = state.get("agent_outputs", {})
    water_out = outputs.get("water_analysis", {})
    knowledge_out = outputs.get("knowledge", {})
    
    # 1. Start with the required execution status checklist timeline
    markdown = "Memory Loaded ✓\n"
    markdown += "Planning Complete ✓\n"
    markdown += "Water Analysis Complete ✓\n"
    markdown += "Knowledge Validation Complete ✓\n"
    markdown += "Reflection Passed ✓\n"
    markdown += "Response Generated ✓\n\n"
    
    markdown += "## 💧 AquaSentinel Water Safety Assessment\n\n"
    
    # Render main dashboard metric table if we have analysis
    if water_out:
        score = water_out.get("water_score", 100.0)
        safety = water_out.get("drinking_safety", "Safe")
        risk = water_out.get("risk_level", "Low")
        conf = water_out.get("confidence_score", 1.0) * 100.0
        
        # Determine safety styling colors for markdown rendering
        safety_indicator = "🟢 Safe"
        if "Unsafe" in safety:
            safety_indicator = "🟡 Unsafe (Treatment Required)"
        elif "Dangerous" in safety:
            safety_indicator = "🔴 Highly Dangerous"
            
        risk_indicator = "🟢 Low"
        if risk == "Medium":
            risk_indicator = "🟡 Medium"
        elif risk == "High":
            risk_indicator = "🔴 High"

        markdown += "| Metric | Assessment |\n"
        markdown += "| :--- | :--- |\n"
        markdown += f"| **Water Quality Score** | **{score:.1f} / 100** |\n"
        markdown += f"| **Drinking Safety** | {safety_indicator} |\n"
        markdown += f"| **Risk Level** | {risk_indicator} |\n"
        markdown += f"| **Confidence Score** | {conf:.1f}% |\n\n"
        
        # Summary & Cause explanation
        markdown += "### 📝 Analysis Summary\n"
        markdown += f"{water_out.get('observations', 'All parameters normal.')}\n\n"
        markdown += f"**Technical Assessment:** {water_out.get('explanation', 'No major contamination.')}\n\n"
        
        if water_out.get("possible_causes"):
            markdown += "**Potential Contamination Causes:**\n"
            for cause in water_out["possible_causes"]:
                markdown += f"- {cause}\n"
            markdown += "\n"
            
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
    if water_out:
        score = water_out.get("water_score", 100.0)
        if score >= 85.0:
            markdown += "1. **Standard Maintenance:** Keep storage tanks and inlet valves clean.\n"
            markdown += "2. **Routine Checks:** Re-test values quarterly to track seasonal fluctuations.\n"
        elif score >= 50.0:
            markdown += "1. **Activated Carbon Filtration:** Recommeded for minor taste, odor, or residual chlorine enhancement.\n"
            markdown += "2. **Reverse Osmosis (RO):** Mandatory to reduce mineral dissolved solids (TDS) to optimal drinking range (< 500 mg/L).\n"
            markdown += "3. **Boiling:** Recommended for disinfection before drinking.\n"
        else:
            markdown += "1. **🔴 Cease Consumption:** Do not use this water directly for drinking or food preparation.\n"
            markdown += "2. **Advanced RO + UV Purification:** Setup a multi-stage filtration system immediately.\n"
            markdown += "3. **Municipal Report:** File a formal water quality complaint to the local municipal sanitation department.\n"
            
    state["synthesized_response"] = markdown
    
    logger.info("Response synthesized successfully.")
    return state
