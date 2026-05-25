from lead_tools import save_lead, list_leads
from admin_product_tools import add_product, update_price, delete_product
from db_tools import get_lead_product_stats

def create_agent_graph():

    def tool_save_lead(state):
        m = state["extracted"]
        return {
            "final_response": save_lead(
                state["user_id"],
                m.get("name"),
                m.get("phone"),
                m.get("contact_pref"),
                m.get("model"),
                m.get("size")
            )
        }

    def tool_list_leads(state):
        return {"final_response": list_leads()}

    def tool_add_product_node(state):
        m = state["extracted"]
        return {
            "final_response": add_product(
                m.get("model"),
                m.get("size"),
                m.get("price")
            )
        }

    def tool_update_price_node(state):
        m = state["extracted"]
        return {
            "final_response": update_price(
                m.get("model"),
                m.get("size"),
                m.get("price")
            )
        }

    def tool_delete_product_node(state):
        m = state["extracted"]
        return {
            "final_response": delete_product(
                m.get("model"),
                m.get("size")
            )
        }

    def tool_analytics_node(state):
        stats = get_lead_product_stats()
        if not stats:
            return {"final_response": "No analytics available."}

        lines = [
            f"{s['model']} {s['size']}: {s['count']} leads"
            for s in stats
        ]
        return {"final_response": "\n".join(lines)}

    # Return a simple dispatch table
    return {
        "save_lead": tool_save_lead,
        "list_leads": tool_list_leads,
        "admin_add_product": tool_add_product_node,
        "admin_update_price": tool_update_price_node,
        "admin_delete_product": tool_delete_product_node,
        "admin_analytics": tool_analytics_node,
    }
