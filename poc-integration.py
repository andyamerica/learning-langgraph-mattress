import operator
from typing import Annotated, TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, END

# --- 1. MOCK BIM LAYER (The Revit / Speckle Side) ---
class MockSpeckleClient:
    """Simulates receiving data from a Revit Baseplate Family via Speckle."""
    @staticmethod
    def get_baseplate_data(element_id: str):
        # Simulate a baseplate sent from Revit with analytical loads
        return {
            "elementId": element_id,
            "parameters": {
                "hole_diameter": 19.0,      # mm
                "edge_distance": 48.0,      # mm
                "concrete_grade": "C30/37"
            },
            "analytical_loads": {
                "tension_force": 32.5       # kN
            }
        }

    @staticmethod
    def update_revit_element(element_id: str, anchor_name: str, util: float):
        # Simulate writing data back to Revit parameters
        print(f"\n[BIM UPDATE] Element {element_id}: Parameter 'Comments' set to 'Confirmed: {anchor_name}'")
        print(f"[BIM UPDATE] Element {element_id}: Parameter 'Utilization' set to {util*100}%")

# --- 2. MOCK ENGINEERING LAYER (The Hilti Side) ---
class MockHiltiEngine:
    """Simulates the Hilti PROFIS Engineering Calculation Engine."""
    @staticmethod
    def calculate(anchor_type: str, tension: float):
        # Anchor capacities (Simplified for PoC)
        capacities = {"M10": 12.0, "M12": 22.0, "M16": 40.0, "M20": 65.0}
        capacity = capacities.get(anchor_type, 0.0)
        utilization = tension / capacity if capacity > 0 else 99.9
        return {
            "utilization": round(utilization, 2),
            "status": "PASS" if utilization <= 1.0 else "FAIL"
        }

# --- 3. LANGGRAPH ORCHESTRATION ---

class AgentState(TypedDict):
    # The 'State' that flows through the graph
    element_id: str
    bim_data: Dict
    anchor_catalog: List[str]
    current_anchor_idx: int
    decision_log: List[str]
    final_design: Optional[Dict]
    status: str

# Node 1: Extract Data from BIM
def extract_bim_node(state: AgentState):
    print(f"--- Extracting Data for Element {state['element_id']} ---")
    data = MockSpeckleClient.get_baseplate_data(state["element_id"])
    return {"bim_data": data, "decision_log": ["Data extracted from Revit via Speckle."]}

# Node 2: Check Geometry (Anchor vs Hole)
def geometry_check_node(state: AgentState):
    anchor = state["anchor_catalog"][state["current_anchor_idx"]]
    anchor_dia = int(anchor[1:]) # Extract '16' from 'M16'
    hole_dia = state["bim_data"]["parameters"]["hole_diameter"]
    
    if anchor_dia > hole_dia:
        log = f"Geometry: {anchor} is too large for {hole_dia}mm hole. FAILED."
        return {"status": "GEOM_FAIL", "decision_log": state["decision_log"] + [log]}
    
    log = f"Geometry: {anchor} fits {hole_dia}mm hole. PASSED."
    return {"status": "GEOM_PASS", "decision_log": state["decision_log"] + [log]}

# Node 3: Structural Analysis
def structural_calc_node(state: AgentState):
    if state["status"] == "GEOM_FAIL": return state
    
    anchor = state["anchor_catalog"][state["current_anchor_idx"]]
    tension = state["bim_data"]["analytical_loads"]["tension_force"]
    
    result = MockHiltiEngine.calculate(anchor, tension)
    log = f"Structural: {anchor} Utility at {result['utilization']*100}% -> {result['status']}"
    
    return {
        "status": result["status"],
        "final_design": {"anchor": anchor, "util": result["utilization"]} if result["status"] == "PASS" else None,
        "decision_log": state["decision_log"] + [log]
    }

# Node 4: Update BIM Model
def update_bim_node(state: AgentState):
    design = state["final_design"]
    MockSpeckleClient.update_revit_element(state["element_id"], design["anchor"], design["util"])
    
    return {"decision_log": state["decision_log"] + ["BIM model updated successfully."]}

# Router Logic
def iteration_router(state: AgentState):
    if state["status"] == "PASS":
        return "update_bim"
    
    if state["current_anchor_idx"] < len(state["anchor_catalog"]) - 1:
        print(f"Upsizing from {state['anchor_catalog'][state['current_anchor_idx']]}...")
        return "next_anchor"
    
    return "abort"

# --- 4. GRAPH CONSTRUCTION ---

workflow = StateGraph(AgentState)

workflow.add_node("extract", extract_bim_node)
workflow.add_node("check_geom", geometry_check_node)
workflow.add_node("calc_struct", structural_calc_node)
workflow.add_node("update_bim", update_bim_node)
workflow.add_node("upsize", lambda state: {"current_anchor_idx": state["current_anchor_idx"] + 1})

workflow.set_entry_point("extract")
workflow.add_edge("extract", "check_geom")
workflow.add_edge("check_geom", "calc_struct")

workflow.add_conditional_edges(
    "calc_struct",
    iteration_router,
    {
        "update_bim": "update_bim",
        "next_anchor": "upsize",
        "abort": END
    }
)

workflow.add_edge("upsize", "check_geom")
workflow.add_edge("update_bim", END)

app = workflow.compile()

# --- 5. EXECUTION ---
if __name__ == "__main__":
    inputs = {
        "element_id": "REVIT-BP-9921",
        "anchor_catalog": ["M10", "M12", "M16", "M20"],
        "current_anchor_idx": 0,
        "decision_log": [],
        "status": "init"
    }

    final_output = app.invoke(inputs)

    print("\n--- DECISION LOG ---")
    for step in final_output["decision_log"]:
        print(f"• {step}")