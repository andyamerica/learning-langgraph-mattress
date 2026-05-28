Architecture Evolution & Rationale
A concise history of why the system evolved from a simple LangGraph bot into a memory‑aware, quota‑efficient conversational engine.

1. 🚦 Where We Started
The project began as a pure LangGraph + rule-based router with:

No LLM extraction

No conversational memory

No user identity

No quota awareness

No context continuity

Pros
Fast

Cheap

Simple

Cons
Could not understand natural language

No follow‑up questions (“What about queen?”)

No per‑user state

No ability to scale beyond one user

Hard to extend

This pushed us toward a more flexible architecture.

2. 🧠 Why We Introduced LLM Extraction
We added an LLM‑based extractor (extract_query()) to parse:

intent

model

size

phone

admin commands

Pros
Natural language understanding

Flexible inputs (“I want a 6x6 mattress”)

Cleaner routing logic

Cons
Every message triggered an LLM call

No quota protection

No memory → repeated questions

This led to the next step.

3. 👤 Why We Added User Identity
Originally, memory was global, meaning:

All users shared the same state

One user’s “king” became another user’s “king”

Impossible to scale

We introduced:

Default identity = Telegram chat ID

Optional upgrade = phone number

Pros
True per‑user memory

Lead tracking tied to phone

Multi‑user safe

Cons
Required refactoring router signature

Needed a memory store

This enabled conversational memory.

4. 🧩 Why We Added Conversational Memory
We introduced a tiny per‑user memory dict:

json
{
  "model": "...",
  "size": "...",
  "last_intent": "..."
}
Pros
Follow‑up questions work

Memory stays tiny (no bloat)

No long-term logs

Easy to reset on catalog/restart

Cons
Still calls LLM too often

Needed intent separation rules

This set the stage for quota‑aware routing.

5. ⚡ Why We Added Quota‑Aware Routing
Gemini quota is limited.
Calling the LLM for every message is expensive and unnecessary.

We added rule-based shortcuts for:

catalog

price queries using SIZE_ALIASES

greetings

restart

simple commands

Pros
70–80% fewer LLM calls

Faster responses

Cheaper operation

Cleaner logic

Cons
Requires maintaining alias dictionaries

Needs careful ordering of shortcuts

This dramatically reduced LLM usage.

6. 📦 Why We Will Add Summarization Hooks
Not implemented yet — but planned.

Purpose:

Prepare for long-term memory

Avoid future refactoring

Allow summarizing old interactions

Pros
Future‑proof

No behavior change today

Cons
Adds a placeholder function

This is a tiny, safe enhancement.

7. 🧱 Final Architecture Principles
The system now follows these rules:

1. Use LLM only when needed
If a rule-based shortcut can answer → skip LLM.

2. Memory updates only for context-bearing intents
get_price

mattress details

model details

comparisons

3. Memory resets only for fresh-start intents
show_catalog

restart

4. Memory preserved for non-context intents
greetings

admin

small talk

5. Identity always comes first
Phone > Telegram chat ID.

8. 🚀 The Result
You now have a system that is:

Scalable (per-user memory)

Efficient (quota-aware routing)

Natural (LLM extraction only when needed)

Predictable (clear intent separation)

Extensible (summarization hooks ready)

This is a solid foundation for future features like:

analytics

fuzzy matching

richer product details

lead scoring



///
Architecture Evolution & System Rationale
A concise, visual history of how the system evolved from a simple LangGraph bot into a memory‑aware, quota‑efficient conversational engine.

1. Initial System — “Simple LangGraph Bot”
Code
User → Telegram → bot.py → LangGraph → Response
Pros

Fast

Cheap

Simple

Cons

No natural language understanding

No follow‑ups (“What about queen”)

No per‑user memory

Not multi‑user safe

2. Adding LLM Extraction (extract_query)
Code
User
  ↓
Telegram
  ↓
bot.py
  ↓
route_message()
  ↓
extract_query()  ← LLM parses intent/model/size/phone
  ↓
Handlers
Pros

Natural language understanding

Clean intent routing

Flexible inputs

Cons

Every message triggered LLM

No quota protection

No conversational memory

3. Adding User Identity (Telegram → Phone Upgrade)
Code
User
  ↓
Telegram chat_id (default identity)
  ↓
extract_query() finds phone?
  ↓
If yes → identity = phone
Pros

True per‑user memory

Lead tracking tied to phone

Multi‑user safe

Cons

Required router refactor

Needed memory store

4. Adding Conversational Memory
Code
Per-user memory:
{
  model: "...",
  size: "...",
  last_intent: "..."
}
Pros

Follow‑up questions work

Tiny memory (no bloat)

Predictable resets (catalog/restart)

Cons

Still too many LLM calls

Needed intent separation

5. Adding Quota‑Aware Routing
Code
route_message()
  ↓
[SHORTCUTS]  ← No LLM
  - catalog
  - price via SIZE_ALIASES
  - greetings
  - restart
  ↓
If no shortcut → extract_query() (LLM)
Pros

70–80% fewer LLM calls

Faster responses

Cheaper operation

Cons

Requires alias dictionaries

Requires careful ordering

6. Adding Summarization Hooks (Planned)
Code
Memory → summarize_memory() → compressed state
Pros

Future‑proof

No behavior change today

Cons

Adds placeholder function

7. Final Architecture Principles
1. Use LLM only when needed  
Shortcuts first → LLM second.

2. Memory updates only for context‑bearing intents  
Examples: get_price, mattress details, comparisons.

3. Memory resets only for fresh‑start intents  
Examples: show_catalog, restart.

4. Memory preserved for non‑context intents  
Examples: greetings, admin, small talk.

5. Identity always comes first  
Phone > Telegram chat ID.

8. Final System Diagram
Code
User
  ↓
Telegram
  ↓
bot.py
  ↓
route_message()
      ├── Shortcut Layer (no LLM)
      │       ├── catalog
      │       ├── price via SIZE_ALIASES
      │       ├── greetings
      │       └── restart
      │
      ├── LLM Extraction Layer
      │       └── extract_query()
      │
      ├── Intent Router
      │       ├── get_price
      │       ├── show_catalog
      │       ├── admin tools
      │       └── general Q&A
      │
      └── Memory Manager
              ├── load per-user memory
              ├── update/reset as needed
              └── save per-user memory
9. Resulting System
Scalable (per‑user memory)

Efficient (quota‑aware routing)

Natural (LLM only when needed)

Predictable (intent separation)

Extensible (summarization hooks ready)