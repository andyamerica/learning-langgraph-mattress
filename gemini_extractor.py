import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are a mattress sales assistant. Extract structured fields from the user message.

Return a JSON object with:
- intent: one of ["get_price", "show_catalog", "general_question"]
- model: one of ["Luxury", "Essential", "Base", null]
- size: one of ["6x6", "6x7", "5x6", null]

Rules:
- If the user mentions both a model and a size (in ANY order), intent MUST be "get_price".
- If the user mentions only a model, intent = "get_price" and size = null.
- If the user mentions only a size, intent = "get_price" and model = null.

Synonyms:
- "king" → "6x6"
- "super king", "superking" → "6x7"
- "queen" → "5x6"
- "premium", "top", "high end" → "Luxury"
- "mid", "midrange", "middle" → "Essential"
- "cheap", "budget", "basic" → "Base"

Examples:
- "king luxury" → {"intent": "get_price", "model": "Luxury", "size": "6x6"}
- "luxury king" → {"intent": "get_price", "model": "Luxury", "size": "6x6"}
- "price of essential queen" → {"intent": "get_price", "model": "Essential", "size": "5x6"}

"intent": one of [
    "get_price",
    "show_catalog",
    "general_question",
    "save_lead",
    "list_leads",
    "admin_status",
    "admin_restart"
]

"name": string | null,
"phone": string | null,
"contact_pref": string | null

Return ONLY valid JSON.

FORMAT RULES (CRITICAL):
- Output MUST be a single raw JSON object.
- Do NOT wrap the JSON in ```json, ``` or any other Markdown fences.
- Do NOT include code blocks, explanations, comments, or text outside the JSON.
- Do NOT include phrases like “Here is the JSON” or “Sure, here you go”.
- The response MUST be valid JSON that can be parsed directly.

"""

def extract_query(user_text):
    print("DEBUG — Using model:", os.getenv("GEMINI_MODEL"))
    print("DEBUG — SYSTEM_PROMPT length:", len(SYSTEM_PROMPT))

    text = user_text.lower()

    # -----------------------------
    # 1. Admin commands (bypass Gemini)
    # -----------------------------
    if text.startswith("/admin"):
        if "status" in text:
            return {
                "intent": "admin_status",
                "model": None,
                "size": None,
                "name": None,
                "phone": None,
                "contact_pref": None
            }
        if "restart" in text:
            return {
                "intent": "admin_restart",
                "model": None,
                "size": None,
                "name": None,
                "phone": None,
                "contact_pref": None
            }

    # -----------------------------
    # 2. Lead-related rule-based detection
    # -----------------------------
    if "my name is" in text or "contact me" in text:
        return {
            "intent": "save_lead",
            "model": None,
            "size": None,
            "name": None,
            "phone": None,
            "contact_pref": None
        }

    if "show leads" in text or "list leads" in text:
        return {
            "intent": "list_leads",
            "model": None,
            "size": None,
            "name": None,
            "phone": None,
            "contact_pref": None
        }

    if "/admin add" in text:
        return {"intent": "admin_add_product"}

    if "/admin update" in text:
        return {"intent": "admin_update_price"}

    if "/admin delete" in text:
        return {"intent": "admin_delete_product"}

    if "/admin analytics" in text:
        return {"intent": "admin_analytics"}

    # Create model with system prompt
    model = genai.GenerativeModel(
        model_name=os.getenv("GEMINI_MODEL"),
        system_instruction=SYSTEM_PROMPT
    )

    # Correct Messages API format
    response = model.generate_content(
        [
            {"role": "user", "parts": text}
        ]
    )

    raw = response.text.strip()
    print("DEBUG — Raw model output:", raw)

    # --- CLEAN MARKDOWN FENCES ---
    cleaned = re.sub(r"^```[a-zA-Z]*", "", raw)
    cleaned = re.sub(r"```$", "", cleaned).strip()

    print("DEBUG — Cleaned JSON:", cleaned)

    # --- PARSE JSON SAFELY ---
    try:
        data = json.loads(cleaned)
    except Exception as e:
        print("DEBUG — JSON parse error:", e)
        return {"intent": "general_question", "model": None, "size": None}

    # --- NORMALIZE KEYS ---
    intent = data.get("intent", "general_question")
    model_name = data.get("model")
    size = data.get("size")

    result = {
        "intent": intent,
        "model": model_name,
        "size": size,
        "name": data.get("name"),
        "phone": data.get("phone"),
        "contact_pref": data.get("contact_pref")
    }

    print("DEBUG — Extraction result:", result)
    return result
