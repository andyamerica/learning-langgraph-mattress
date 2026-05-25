from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from data import PRODUCT_FAMILIES, SIZES, PRICES, CATALOG, FAQS

# -----------------------------
# STATE DEFINITION
# -----------------------------
class State(TypedDict):
    user_input: str
    model: Optional[str]
    size: Optional[str]
    response: Optional[str]


# -----------------------------
# ROUTER
# -----------------------------
def router(state: State):
    text = state["user_input"].lower()

    pricing_keywords = ["price", "cost", "how much", "rate", "charge"]
    model_keywords = ["luxury", "essential", "base"]
    size_keywords = ["6x6", "6x7", "5x6", "king", "super king", "superking", "queen"]

    if any(k in text for k in pricing_keywords):
        return {"next": "pricing"}

    if any(k in text for k in model_keywords + size_keywords):
        return {"next": "pricing"}

    if "catalog" in text or "sizes" in text:
        return {"next": "catalog"}

    return {"next": "qa"}


# -----------------------------
# PRICING AGENT (WITH MEMORY)
# -----------------------------
def pricing_agent(state: State):
    text = state["user_input"].lower()

    model = state.get("model")
    size = state.get("size")

    # MODEL EXTRACTION
    if not model:
        if "luxury" in text:
            model = "Luxury"
        elif "essential" in text:
            model = "Essential"
        elif "base" in text:
            model = "Base"

    # SIZE EXTRACTION
    if not size:
        if "6x6" in text or "king" in text:
            size = "6x6"
        elif "6x7" in text or "super king" in text or "superking" in text:
            size = "6x7"
        elif "5x6" in text or "queen" in text:
            size = "5x6"

    # PRICE LOOKUP
    if model and size:
        price = PRICES.get((model, size))
        return {
            "model": model,
            "size": size,
            "response": f"The price of the {model} mattress ({size}) is ${price}."
        }

    if model and not size:
        return {
            "model": model,
            "size": None,
            "response": f"Which size of the {model} mattress? (King, Super King, Queen)"
        }

    if size and not model:
        return {
            "model": None,
            "size": size,
            "response": f"Which model for size {size}? (Luxury, Essential, Base)"
        }

    return {
        "model": model,
        "size": size,
        "response": "I couldn't identify the mattress model or size."
    }


# -----------------------------
# CATALOG AGENT
# -----------------------------
def catalog_agent(state: State):
    lines = [f"{item['model']} {item['size_code']} – ${item['price']}" for item in CATALOG]
    return {"response": "\n".join(lines)}


# -----------------------------
# QA AGENT
# -----------------------------
def qa_agent(state: State):
    text = state["user_input"].lower()
    for faq in FAQS:
        if any(word in text for word in faq["question"].split()):
            return {"response": faq["answer"]}
    return {"response": "I can help with mattress types, pricing, or catalog details."}


# -----------------------------
# GRAPH SETUP (THE FIX IS HERE)
# -----------------------------
graph = StateGraph(
    State,
    merge=lambda old, new: {**old, **new}   # <-- THIS FIXES YOUR BOT
)

graph.add_node("router", router)
graph.add_node("pricing", pricing_agent)
graph.add_node("catalog", catalog_agent)
graph.add_node("qa", qa_agent)

graph.set_entry_point("router")

graph.add_conditional_edges(
    "router",
    lambda x: x["next"],
    {"pricing": "pricing", "catalog": "catalog", "qa": "qa"}
)

graph.add_edge("pricing", END)
graph.add_edge("catalog", END)
graph.add_edge("qa", END)

app = graph.compile()
