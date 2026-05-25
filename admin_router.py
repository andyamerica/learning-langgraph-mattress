from agent_graph import create_agent_graph

# Compile the agent once
agent = create_agent_graph()

# -----------------------------
# Run admin command through agent
# -----------------------------
async def handle_admin_command(user_id: str, text: str):
    text_lower = text.lower()

    # Map Telegram text → agent intent
    if "status" in text_lower:
        intent = "admin_status"
    elif "leads" in text_lower:
        intent = "list_leads"
    elif "restart" in text_lower:
        intent = "admin_restart"
    elif "add" in text_lower:
        intent = "admin_add_product"
    elif "update" in text_lower:
        intent = "admin_update_price"
    elif "delete" in text_lower:
        intent = "admin_delete_product"
    elif "analytics" in text_lower:
        intent = "admin_analytics"
    else:
        return "Unknown admin command."

    # Build agent state
    state = {
        "user_id": user_id,
        "user_message": text,
        "intent": intent,
        "extracted": {},   # admin commands don't need extraction
    }

    # Run agent
    result = agent.invoke(state)
    return result.get("final_response", "No response.")
