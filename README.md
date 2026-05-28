# 🛏️ Mattress Bot — Conversational AI System

A Telegram-based conversational agent that helps users explore mattress models, check prices, browse the catalog, and submit leads.  
The system uses a hybrid architecture combining:

- LLM-powered extraction  
- A deterministic router  
- SQLite-backed product data  
- Agent-based admin tools  
- A normalization layer  
- Short-term conversational memory  

---

## 📂 Project Structure

my-engineering-project/
│
├── bot.py                     # Telegram bot entrypoint
├── mattress_router.py         # Router, normalization, handlers
├── gemini_extractor.py        # LLM-based extraction
├── db_tools.py                # SQLite helpers
├── agent_graph.py             # Admin + lead agent tools
├── admin_product_tools.py     # Admin product management
├── lead_tools.py              # Lead saving/listing
│
├── init_db.py                 # DB initialization
├── master_data.sql            # Product + catalog seed data
├── mattress.db                # SQLite database
│
├── requirements.txt
└── .env


---

## 🔄 System Flow

1. User sends a message via Telegram  
2. `bot.py` forwards text to `route_message()`  
3. Router calls `extract_query()` → LLM returns structured JSON  
4. Router normalizes model/size and updates memory  
5. Router dispatches to the correct handler  
6. Handler queries SQLite  
7. Response is returned to Telegram  

---

## 🧠 Conversational Memory (Current)

- Stores last model, size, and intent  
- Overwritten each turn (no bloat)  
- Enables follow-up questions like “What about Queen”  

---

## 🧩 Planned Enhancements (Feature Branch)

- **User identity system**  
  - Default: Telegram chat ID  
  - Optional: upgrade to phone number  
- **Memory manager**  
  - Per-user memory  
  - Cleaner API  
- **Quota-aware router**  
  - Skip LLM when possible  
  - Rule-based shortcuts  
  - Graceful fallback  
- **Token summarization hooks**  
  - For future long-term memory  

---

## 🧪 Testing

- `test_db_check.py` verifies DB integrity  
- Manual Telegram testing for conversational flow  

---

## 🚀 Roadmap

- Conversational memory upgrade  
- User identity linking  
- Quota-aware routing  
- Admin analytics  
- Model normalization + fuzzy matching  
