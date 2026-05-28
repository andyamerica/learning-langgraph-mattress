Full System Architecture & Router Logic (Updated with Model–Size Inference)
1. High‑Level Architecture

User → Telegram Bot → Router → Extractor (Gemini)
     → Normalization → Inference → Handlers → SQLite DB → Response

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
┌──────────────────────────────────────────────┐
│                 Router Layer                 │
│ - quota-aware shortcuts (no LLM)             │
│ - extract_text()                             │
│ - normalize_size()                           │
│ - model–size inference                       │
│ - memory (per-user)                          │
│ - identity upgrade (phone)                   │
│ - intent routing                             │
└───────────────┬──────────────────────────────┘
                │
                ▼
┌──────────────────────────────┐
│     Extractor (Gemini)       │
│  extract_query(user_text)    │
│  → intent, model, size, phone│
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────────────────────┐
│            Business Logic Layer              │
│ - handle_get_price()                         │
│ - handle_show_catalog()                      │
│ - handle_general_question()                  │
│ - agent-based admin + lead tools             │
└───────────────┬──────────────────────────────┘
                │
                ▼
┌──────────────────────────────┐
│        Database Layer        │
│         (SQLite)             │
│ - products                   │
│ - catalog                    │
│ - leads                      │
└──────────────────────────────┘

2. System Components
    a. Telegram Bot
        Receives user messages
        Sends responses
        Forwards text to the router

    b. Router (mattress_router.py)
    The brain of the system:
        Quota‑aware shortcuts (no LLM)
        LLM extraction
        Model–size inference
        Memory management
        Identity upgrade (phone)
        Intent routing
        Agent graph integration

    c. Extractor (gemini_extractor.py)
        Converts user text → structured JSON
        Extracts:
            intent, model, size, phone and free‑text fields

    c. Normalization Layer
        normalize_size()
        extract_text()
        SIZE_ALIASES mapping

    d. Handlers
        handle_get_price()
        handle_show_catalog()
        handle_general_question()

    e. Agent Graph
        Admin tools
        Lead tools
        Runs only for admin/lead intents

    f. SQLite Database
        Tables: products, catalog, leads

3. Router Flow (Full Detail)
    ┌──────────────────────────────────────────────┐
    │                route_message()               │
    └──────────────────────────────────────────────┘
    
    a. STEP 1 — Load Memory
        Retrieve per‑user memory
        Ensure last_intent exists
    
    b. STEP 2 — QUOTA‑AWARE SHORTCUTS (NO LLM)
        These run before extraction to save cost.
        
        1. Direct price shortcut (size keyword match)
            If user says “king”, “queen”, “6x6”, etc.
                Immediately return price
                No LLM
                No inference
                No clarifying questions

        2. Catalog shortcut
            If user says “catalog”
                Return catalog immediately

        3. Greetings
            “hi”, “hello”, “thanks”, etc.

        4. Restart
            “restart”, “start over”

        If any shortcut triggers → return immediately.

    c. STEP 3 — LLM EXTRACTION
        extraction = extract_query(user_text)
        intent = extraction["intent"]

        Extractor returns:
            intent, model, size, phone, free‑text fields

    d. STEP 4 — MODEL–SIZE INFERENCE (NEW)
        Runs before memory fill.

        Cases:

            1. Missing both model & size
            → Ask user to specify both

            2. Missing model
            → Ask: “Which model for size X?”

            3. Missing size
            → Ask: “Which size of the MODEL mattress?”

            4. Both present
            → Continue to price lookup

        This makes the bot behave like a real salesperson.

    e. STEP 5 — Identity Upgrade (Phone Number)
        If extractor finds a phone number:
            Replace user_id with phone
            Load memory for that phone

        This allows:
            lead tracking
            multi‑device continuity

    f. STEP 6 — Memory Fill
        model = extracted_model or memory["model"]
        size  = extracted_size  or memory["size"]

        This allows:
            follow‑up questions
            conversational continuity
    g. STEP 7 — Agent‑Based Intents
        If intent is:
            save_lead
            list_leads
            admin_status
            admin_restart
        → Forward to agent graph
        → No memory changes

    h. STEP 8 — LLM‑Based Price Lookup
        This is the real price handler:
        
        if intent == "get_price":
            response = handle_get_price(model, size)
        Uses:
            model–size inference
            memory
            normalization
            SQLite lookup
    
    i. STEP 9 — LLM‑Based Catalog
        If intent is show_catalog:
            Return catalog
            Reset memory
            
    j. STEP 10 — General Fallback
        If nothing else matches:
            Return general help message
            Keep memory unchanged

4. Memory System
    Stored per user:
        Code
        {
        "model": "Luxury",
        "size": "King",
        "last_intent": "get_price"
        }

    Memory is updated when:
        Price lookup
        Catalog
        Restart
        Shortcut price lookup

    Memory is NOT updated when:
        Greetings
        General questions
        Agent intents

    Summarization Hook
    new_memory = summarize_memory(new_memory)  

    Currently a passthrough, but ready for:
        compression
        pruning
        quota management

5. Model–Size Inference (Detailed)

    Extractor output example:
        {
        "intent": "get_price",
        "model": "Luxury",
        "size": null
        }
    Inference logic:
        If model missing → ask for model
        If size missing → ask for size
        If both missing → ask for both
        If both present → continue

    Why inference runs BEFORE memory fill
        Because memory might contain stale values.
        Inference must use only what the user said now.

6. File Structure (Updated)
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
    ├── .env
    │
    └── mattress_bot_summary.md   ← (THIS FILE)

7. Example Conversation Flows

    Flow 1 — Direct Price Shortcut
        User: “How much is king?”
        Router: shortcut → price → done

    Flow 2 — LLM Price with Inference
        User: “Luxury mattress”
        Extractor: model=Luxury, size=None
        Inference: ask for size

    Flow 3 — Memory Fill
        User: “King”
        Memory: model=Luxury
        Price lookup → return price

    Flow 4 — Lead Saving
        User: “My number is 555‑1234”
        Extractor: phone=555‑1234
        Identity upgrade → memory moves to phone

8. How to Re‑Prompt Copilot Using This File
    Paste this into a new chat:
        I am working on a mattress pricing Telegram bot.  
        Here is the full system architecture and router logic:  
        <PASTE THE CONTENTS OF mattress_bot_summary.md>  

        Please continue helping me with the next step.
    
    This restores full context instantly.

9. Next Steps (Recommended Order)
    Test the bot on Telegram
    Add Lead Enrichment
    Add Natural Language Catalog Search