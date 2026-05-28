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

USER_MEMORY = {}

def summarize_memory(memory: dict) -> dict:
    return memory

def normalize_size(size: str | None):
    if not size:
        return None
    s = size.lower().strip()
    return SIZE_ALIASES.get(s, size)

def extract_text(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return (value.get("text") or value.get("value") or value.get("raw") or "").strip()
    return None

def handle_get_price(model: str | None, size: str | None) -> str:
    """
    Strict price handler:
    - NEVER guesses missing size or model
    - ALWAYS asks for missing info
    - ONLY returns a price when both model + size are present
    """

    # Normalize inputs
    model = model.strip().title() if model else None
    size  = normalize_size(size) if size else None

    # Missing both
    if not model and not size:
        return (
            "Which mattress are you interested in? "
            "You can mention model and size, like 'Luxury king'."
        )

    # Missing model
    if not model and size:
        return (
            f"Which model for size {size}? "
            "(Luxury, Essential, Base)"
        )

    # Missing size
    if model and not size:
        return (
            f"Which size of the {model} mattress? "
            "(King, Super King, Queen)"
        )

    # Both present → lookup
    price = get_price(model, size)

    if price is None:
        return f"I couldn't find a price for {model} {size}."

    return f"The price of the {model} mattress ({size}) is ${price:.2f}."


def handle_show_catalog():
    items = get_catalog()
    if not items:
        return "The catalog is empty."

    lines = [f"• {item['model']}: {item['description']}" for item in items]
    return "\n".join(lines)

def handle_general_question(user_text: str) -> str:
    return (
        "I can help with mattress prices and catalog.\n"
        "Try asking things like:\n"
        "- 'Price of luxury king'\n"
        "- 'Show me your catalog'\n"
        "- 'How much is base queen?'"
    )

def get_memory(user_id: str):
    return USER_MEMORY.get(user_id, {})

def set_memory(user_id: str, memory: dict):
    USER_MEMORY[user_id] = memory

def route_message(user_text: str, user_id: str):

    memory = get_memory(user_id) or {}
    memory.setdefault("last_intent", None)

    text = user_text.lower()

    # -----------------------------------------
    # QUOTA-AWARE SHORTCUTS (NO LLM)
    # -----------------------------------------

    # 1) Direct price shortcut (e.g. "6x6", "king", etc.)
    for key, normalized_size in SIZE_ALIASES.items():
        if key in text:
            size = normalized_size
            model = memory.get("model")  # Use memory if available

            # If no model yet, ask for it but STORE the size
            if not model:
                new_memory = {
                    "model": memory.get("model"),
                    "size": size,
                    "last_intent": "get_price",
                }
                new_memory = summarize_memory(new_memory)
                set_memory(user_id, new_memory)
                return (
                    f"Which model for size {size}? (Luxury, Essential, Base)"
                ), new_memory

            # Normalize before lookup
            model = model.strip().title()
            size = size.strip().title()

            response = handle_get_price(model, size)

            new_memory = {
                "model": model,
                "size": size,
                "last_intent": "get_price"
            }

            new_memory = summarize_memory(new_memory)
            set_memory(user_id, new_memory)
            return response, new_memory

    # 2) Catalog shortcut
    if "catalog" in text:
        response = handle_show_catalog()

        new_memory = {
            "model": None,
            "size": None,
            "last_intent": "show_catalog"
        }

        new_memory = summarize_memory(new_memory)
        set_memory(user_id, new_memory)
        return response, new_memory

    # 3) Greetings
    if text in ["hi", "hello", "hey", "thanks", "thank you"]:
        response = handle_general_question(user_text)
        set_memory(user_id, memory)
        return response, memory

    # 4) Restart
    if "restart" in text or "start over" in text:
        new_memory = {
            "model": None,
            "size": None,
            "last_intent": "restart"
        }

        new_memory = summarize_memory(new_memory)
        set_memory(user_id, new_memory)
        return "Okay, starting fresh!", new_memory

    # -----------------------------------------
    # LLM EXTRACTION
    # -----------------------------------------

    extraction = extract_query(user_text)
    intent = extraction["intent"]

    # -----------------------------------------
    # IDENTITY UPGRADE (phone number)
    # -----------------------------------------

    extracted_phone = extract_text(extraction.get("phone"))
    if extracted_phone:
        user_id = extracted_phone
        memory = get_memory(user_id) or {}
        memory.setdefault("last_intent", None)

    # -----------------------------------------
    # MERGED MEMORY (this is the key fix)
    # -----------------------------------------

    extracted_model = extract_text(extraction.get("model"))
    extracted_size  = extract_text(extraction.get("size"))

    merged_memory = {
        "model": extracted_model or memory.get("model"),
        "size":  extracted_size  or memory.get("size"),
        "last_intent": intent or memory.get("last_intent"),
        "name": extract_text(extraction.get("name")) or memory.get("name"),
        "phone": extracted_phone or memory.get("phone"),
        "contact_pref": extract_text(extraction.get("contact_pref")) or memory.get("contact_pref"),
    }

    model = merged_memory["model"]
    size  = merged_memory["size"]

    # -----------------------------------------
    # Agent-based intents
    # -----------------------------------------
    if intent in ["save_lead", "list_leads", "admin_status", "admin_restart"]:
        state = {
            "user_id": user_id,
            "user_message": user_text,
            "intent": intent,
            "extracted": extraction,
        }
        result = agent.invoke(state)
        # keep merged_memory
        set_memory(user_id, merged_memory)
        return result["final_response"], merged_memory

    # -----------------------------------------
    # MODEL–SIZE INFERENCE (using merged memory)
    # -----------------------------------------
    if intent == "get_price":

        # Case 1: missing both
        if not model and not size:
            set_memory(user_id, merged_memory)
            return (
                "Which mattress are you interested in? "
                "You can mention model and size, like 'Luxury king'."
            ), merged_memory

        # Case 2: missing model
        if not model and size:
            set_memory(user_id, merged_memory)
            return (
                f"Which model for size {size.title()}? "
                "(Luxury, Essential, Base)"
            ), merged_memory

        # Case 3: missing size
        if model and not size:
            set_memory(user_id, merged_memory)
            return (
                f"Which size of the {model.title()} mattress? "
                "(King, Super King, Queen)"
            ), merged_memory

        # Case 4: both present → continue to price lookup
        # If BOTH model + size exist → NOW call get_price()
        #price = get_price(model, size)

        # Normalize before DB lookup
        model_norm = model.strip().title()
        size_norm  = size.strip().title()

        response = handle_get_price(model_norm, size_norm)

        final_memory = {
            "model": model_norm,
            "size": size_norm,
            "last_intent": intent,
            "name": merged_memory.get("name"),
            "phone": merged_memory.get("phone"),
            "contact_pref": merged_memory.get("contact_pref"),
        }

        final_memory = summarize_memory(final_memory)
        set_memory(user_id, final_memory)
        return response, final_memory

    # -----------------------------------------
    # Catalog (LLM-based)
    # -----------------------------------------
    if intent == "show_catalog":
        response = handle_show_catalog()

        new_memory = {
            "model": None,
            "size": None,
            "last_intent": intent,
            "name": merged_memory.get("name"),
            "phone": merged_memory.get("phone"),
            "contact_pref": merged_memory.get("contact_pref"),
        }

        new_memory = summarize_memory(new_memory)
        set_memory(user_id, new_memory)
        return response, new_memory

    # -----------------------------------------
    # General question (fallback)
    # -----------------------------------------
    response = handle_general_question(user_text)
    set_memory(user_id, merged_memory)
    return response, merged_memory

