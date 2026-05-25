#from mattress_master_data import PRICES, CATALOG
import google.generativeai as genai
from gemini_extractor import genai
from gemini_extractor import extract_query
from agent_graph import create_agent_graph
from db_tools import get_price, get_catalog

agent = create_agent_graph()

SIZE_ALIASES = {
    "king": "King",
    "6x6": "King",
    "6 x 6": "King",
    "6 ft": "King",
    "6ft": "King",
    "6 feet": "King",

    "queen": "Queen",
    "5x6": "Queen",
    "5 x 6": "Queen",

    "super king": "Super King",
    "7x7": "Super King",
    "7 x 7": "Super King"
}

def normalize_size(size: str | None):
    if not size:
        return None
    s = size.lower().strip()
    return SIZE_ALIASES.get(s, size)


def handle_get_price(model: str | None, size: str | None) -> str:
    # Normalize size before doing anything else
    size = normalize_size(size)

    # 1. Missing both
    if not model and not size:
        return "Which mattress are you interested in? You can mention model and size, like 'Luxury king'."

    # 2. Missing model
    if not model and size:
        return f"Which model for size {size}? (Luxury, Essential, Base)"

    # 3. Missing size
    if model and not size:
        return f"Which size of the {model} mattress? (King, Super King, Queen)"

    # 4. Lookup in SQLite
    price = get_price(model, size)

    if price is None:
        return f"I couldn't find a price for {model} {size}."

    # 5. Found
    return f"The price of the {model} mattress ({size}) is ${price:.2f}."

"""
def handle_get_price(model: str | None, size: str | None) -> str:
    if not model and not size:
        return "Which mattress are you interested in? You can mention model and size, like 'Luxury king'."

    if not model and size:
        return f"Which model for size {size}? (Luxury, Essential, Base)"

    if model and not size:
        return f"Which size of the {model} mattress? (King, Super King, Queen)"

    price = PRICES.get((model, size))
    if price is None:
        return f"I couldn't find a price for {model} {size}."

    return f"The price of the {model} mattress ({size}) is ${price}."

"""

"""
def handle_show_catalog() -> str:
    lines = ["Here is our mattress catalog:"]
    for item in CATALOG:
        lines.append(f"- {item['model']} {item['size']} – ${item['price']}")
    return "\n".join(lines)
"""

def handle_show_catalog():
    items = get_catalog()

    if not items:
        return "The catalog is empty."

    lines = []
    for item in items:
        lines.append(f"• {item['model']}: {item['description']}")

    return "\n".join(lines)

def handle_general_question(user_text: str) -> str:
    # Simple fallback – you can later plug Gemini again for QA
    return (
        "I can help with mattress prices and catalog.\n"
        "Try asking things like:\n"
        "- 'Price of luxury king'\n"
        "- 'Show me your catalog'\n"
        "- 'How much is base queen?'"
    )


def route_message(user_text: str, memory: dict | None = None) -> tuple[str, dict]:
    if memory is None:
        memory = {"model": None, "size": None}

    extraction = extract_query(user_text)
    intent = extraction["intent"]
    model = extraction["model"] or memory.get("model")
    size = extraction["size"] or memory.get("size")

    # Agent-based intents (NO memory change)
    if intent in ["save_lead", "list_leads", "admin_status", "admin_restart"]:
        state = {
            "user_id": "telegram",
            "user_message": user_text,
            "intent": intent,
            "extracted": extraction,
        }
        result = agent.invoke(state)
        return result["final_response"], memory

    # Price lookup (updates memory)
    if intent == "get_price":
        response = handle_get_price(model, size)
        return response, {"model": model, "size": size}

    # Catalog (resets memory)
    if intent == "show_catalog":
        response = handle_show_catalog()
        return response, {"model": None, "size": None}

    # General question (keep memory)
    response = handle_general_question(user_text)
    return response, memory

"""
def route_message(user_text: str, memory: dict | None = None) -> tuple[str, dict]:

    #memory: {"model": str|None, "size": str|None}
    #Returns: (response_text, updated_memory)

    if memory is None:
        memory = {"model": None, "size": None}

    extraction = extract_query(user_text)
    intent = extraction["intent"]
    model = extraction["model"] or memory.get("model")
    size = extraction["size"] or memory.get("size")

    # -----------------------------
    # Agent-based intents
    # -----------------------------
    if intent == "save_lead":
        state = {
            "user_id": "telegram",   # or pass real user_id if available
            "user_message": user_text,
            "intent": "save_lead",
            "extracted": extraction,
        }
        result = agent.invoke(state)
        return result["final_response"], memory

    if intent == "list_leads":
        state = {
            "user_id": "telegram",
            "user_message": user_text,
            "intent": "list_leads",
            "extracted": {},
        }
        result = agent.invoke(state)
        return result["final_response"], memory

    if intent == "get_price":
        response = handle_get_price(model, size)
        # If we successfully answered a full price, keep memory or reset based on your preference
        return response, {"model": model, "size": size}

    if intent == "show_catalog":
        response = handle_show_catalog()
        # Catalog is a new topic – safe to reset memory
        return response, {"model": None, "size": None}

    # General question
    response = handle_general_question(user_text)
    return response, memory
"""
