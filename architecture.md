This document summarizes the final working architecture, file structure, data flow, memory design, and future enhancements for the Mattress Telegram Bot project. It is designed to be pasted it into a new chat session to restore full context.

1. High level architecture
User → Telegram Bot → Router → Extractor (Gemini)
     → Normalization → Handlers → SQLite DB → Response

┌──────────────────────────────┐
│        Telegram User         │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│       Telegram Bot API       │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│         Router Layer         │
│ - extract_text()             │
│ - normalize_size()           │
│ - memory                     │
│ - intent routing             │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│     Extractor (Gemini)       │
│  extract_query(user_text)    │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│      Business Logic Layer    │
│ - handle_get_price()         │
│ - handle_show_catalog()      │
│ - handle_save_lead()         │
│ - handle_list_leads()        │
│ - admin handlers             │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│        Database Layer        │
│         (SQLite)             │
│ - products                   │
│ - catalog                    │
│ - leads                      │
└──────────────────────────────┘

Components
Telegram Bot — receives/sends messages
Extractor (Gemini) — converts user text → structured JSON
Router (mattress_router.py) — brain of the system
Normalization Layer — fixes messy inputs (e.g., 6x6 → King)
Handlers — price lookup, catalog, leads, admin
SQLite DB — products, catalog, leads
Agent Graph — admin + lead tools

2. File structure
my-engineering-project/
│
├── bot.py
├── mattress_router.py
├── gemini_extractor.py
├── db_tools.py
├── admin_product_tools.py
├── lead_tools.py
├── agent_graph.py
│
├── init_db.py
├── run_master_sql.py
├── load_master_data.py
├── master_data.sql
├── mattress.db
│
├── test_db_check.py
├── requirements.txt
└── .env

3. System flow step-by-step
    1. User sends message → Telegram
    2. bot.py forwards text → route_message()
    3. Router calls extract_query() → Gemini
    4. Extractor returns JSON:
        { intent, model, size, name, phone }
    5. Router:
        - extract_text()
        - normalize_size()
        - memory update
        - dispatch to handler
    6. Handler calls DB tools
    7. DB returns results
    8. Handler formats response
    9. Router returns response + updated memory
    10. bot.py sends message back to Telegram

4. Coversational memory design
Your memory is short‑term, lightweight, and non‑bloated.
{"model": "Luxury", "size": "King"}

✔ Memory is overwritten every turn
Not appended.
Not accumulated.
Not stored long‑term.

✔ Memory is internal
The user never sees it.
✔ Memory is per‑conversation
If you add user_id support, it becomes per‑user.
✔ Memory is used for:
Follow‑up questions
Missing fields
Natural conversation flow
Example:
User: “Luxury King price”
Bot stores: {model: Luxury, size: King}
User: “What about Queen?”
Extractor: {size: Queen}  
Router fills missing model from memory.

5. Normalization Layer
Located in mattress_router.py.
Purpose: Convert messy extractor output → clean DB‑friendly values.
Examples:
“6x6” → “King”
“5x6” → “Queen”
“superking” → “Super King”
This ensures DB lookups always succeed.

6. Handlers
Handlers
Handlers perform the actual business logic:
    handle_get_price()
    handle_show_catalog()
    handle_save_lead()
    handle_list_leads()
    Admin handlers (add/update/delete products)
Handlers:

7. Database Layer (SQLite)
Tables:
    products
    catalog
    leads
Loaded via:
    init_db.py
    run_master_sql.py
    master_data.sql
DB tools:
    get_price()
    get_catalog()
    save_lead()
    list_leads()

8. User Identity (Future Enhancement)
Right now:
user_id = "telegram" (placeholder)

Future Option:
    A. Use Telegram chat ID
        user_id = update.message.chat.id
    B. Use phone number as user_id
        memory["user_id"] = phone
    C. Hybrid
        Telegram ID for session
        Phone number for CRM

9. Token Summarization (Future Enhancement)
Only needed if:
You store long-term conversation history
You store large text chunks
You want persistent memory across sessions

Design:
    Router → Memory Manager → Summarizer → Memory Store
Summarizer periodically compresses:
    old messages
    extracted fields
    user preferences

into a short summary.

10. Next Steps (Optional Enhancements)
    A. Conversational Memory Upgrade
        Store last 3–5 turns
        Summarize older turns
        Persist memory per user

    B. User Identity
        Use Telegram chat ID
        Link phone number to user profile
        Store user preferences

    C. Model Normalization
        “lux”, “luxry”, “luxury mattress” → “Luxury”

    D. Fuzzy Matching
        Handle typos
        Handle partial matches

    E. Admin Analytics
        Most requested models
        Lead conversion stats
        Daily/weekly summaries