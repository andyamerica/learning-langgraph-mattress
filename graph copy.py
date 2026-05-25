from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from data import CATALOG, PRICES, QA

# -------------------------
# State definition
# -------------------------
class State(TypedDict):
    user_input: str
    response: Optional[str]

# -------------------------
# Sub-agents
# -------------------------
def qa_agent(state: State):
    text = state["user_input"].lower()
    if "type" in text:
        return {"response": QA["types"]}
    if "price" in text:
        return {"response": QA["price"]}
    return {"response": "I can help with mattress types, pricing, or catalog details."}

def old_pricing_agent(state: State):
    text = state["user_input"].lower()
    print("PRICING INPUT:", text)

    # naive extraction
    if "luxury" in text and "base" in text and "6x6" in text:
        print("Inside pricing agent: if luxury base and 6x6")
        return {"response": f"The price is ${PRICES[('Luxury','Base','6x6')]}."}

    return {"response": "I couldn't find that exact model/size."}


def pricing_agent(state: State):
    text = state["user_input"].lower()

    # Extract model
    model = None

    if "luxury" in text:
        model = "Luxury"
    elif "essential" in text:
        model = "Essential"
    elif "base" in text:
        model = "Base"

    # Extract size
    size = None
    if "6x6" in text:
        size = "6x6"
    elif "6x7" in text:
        size = "6x7"
    elif "5x6" in text:
        size = "5x6"

    # If both model and size found → return price
    if model and size:
        key = (model, "Base", size) if model != "Base" else (model, model, size)
        # Adjust this key logic based on your PRICES dict structure
        price = PRICES.get(key)

        if price:
            return {"response": f"The price of the {model} mattress ({size}) is ${price}."}
        else:
            return {"response": f"I found {model} {size}, but no price is listed in the catalog."}

    # If model found but size missing
    if model and not size:
        return {"response": f"Which size of the {model} mattress are you interested in? (6x6, 6x7, 5x6)"}

    # If size found but model missing
    if size and not model:
        return {"response": f"Which model are you interested in for size {size}? (Luxury, Essential, Base)"}

    # Nothing matched
    return {"response": "I couldn't identify the mattress model or size. Try something like 'luxury 6x6'."}


def catalog_agent(state: State):
    return {"response": str(CATALOG)}

# -------------------------
# Router (Orchestrator)
# -------------------------
def router(state: State):
    text = state["user_input"].lower()
    print("ROUTER INPUT:", text)

    # Pricing intent keywords
    pricing_keywords = [
        "price", "cost", "how much", "rate", "charge", "what's the price", "what is the price"
    ]

    # Mattress models and sizes (also pricing intent)
    model_keywords = ["luxury", "essential", "base"]
    size_keywords = ["6x6", "6x7", "5x6"]

    # If message contains any pricing keyword → pricing agent
    if any(k in text for k in pricing_keywords):
        return {"next": "pricing"}

    # If message contains a model or size → pricing agent
    if any(k in text for k in model_keywords + size_keywords):
        return {"next": "pricing"}

    # Catalog intent
    if "catalog" in text or "sizes" in text:
        return {"next": "catalog"}

    # Default fallback
    return {"next": "qa"}

# -------------------------
# Build LangGraph
# -------------------------
graph = StateGraph(State)

graph.add_node("qa", qa_agent)
graph.add_node("pricing", pricing_agent)
graph.add_node("catalog", catalog_agent)
graph.add_node("router", router)

graph.set_entry_point("router")

graph.add_conditional_edges(
    "router",
    lambda state: state["next"],
    {
        "qa": "qa",
        "pricing": "pricing",
        "catalog": "catalog"
    }
)

#graph.add_edge("router", "qa")
#graph.add_edge("router", "pricing")
#graph.add_edge("router", "catalog")

graph.add_edge("qa", END)
graph.add_edge("pricing", END)
graph.add_edge("catalog", END)

app = graph.compile()
