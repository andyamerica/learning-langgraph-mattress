You built a Telegram chatbot that extracts structured intent using an LLM, merges that with persistent memory, and routes the conversation through a custom logic engine. Along the way, you learned the difference between deterministic logic (your router, memory, DB lookups) and probabilistic logic (LLM extraction). You discovered why bypassing the LLM for shortcuts is fast but brittle, and why relying on the LLM for everything is flexible but expensive. You debugged a subtle issue where the router was calling the database price lookup too early, causing the system to “guess” King even when the user didn’t specify a size. You learned how memory merging works, why clearing memory too aggressively breaks context, and why keeping memory forever causes the bot to get “stuck” in a state. You now understand the architecture tradeoffs: shortcuts vs. LLM extraction, memory persistence vs. statelessness, and deterministic DB lookups vs. learned models. You also saw how a single misplaced function call (get_price) can override the entire conversational flow. Most importantly, you now have a mental model of how a real conversational system works: extraction → merge → inference → routing → DB → response → memory update. That’s the foundation of every production chatbot, and you’ve built it yourself.

Future:Tell me whether you want to:

build a simple agent

design a full agent architecture

learn how agent loops work

connect agents to your current bot