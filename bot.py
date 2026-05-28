import logging
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from graph import app

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = "REDACTED"

# Store state per user
USER_STATES = {}   # {user_id: state_dict}


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is online and ready!")


async def ping(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong")

def should_reset_memory(user_text: str) -> bool:
    text = user_text.lower()

    model_words = ["luxury", "essential", "base"]
    size_words = ["6x6", "6x7", "5x6", "king", "super king", "superking", "queen"]

    # If message contains model or size → DO NOT reset
    if any(w in text for w in model_words + size_words):
        return False

    # Otherwise → reset memory
    return True


async def handle_message(update, context):
    user_id = update.message.from_user.id
    user_text = update.message.text

    # Load previous state
    state = USER_STATES.get(user_id, {
        "user_input": "",
        "model": None,
        "size": None,
        "response": None
    })

    # If previous response was a final price AND this message is a new topic → reset
    if state.get("response") and "price of the" in state["response"].lower():
        if should_reset_memory(user_text):
            state["model"] = None
            state["size"] = None

    # Update with new input
    state["user_input"] = user_text

    # Run graph
    result = app.invoke(state)

    # Save updated state
    USER_STATES[user_id] = result

    # Send response
    await update.message.reply_text(result["response"])


def main():
    print(">>> inside main()")
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(">>> running polling")
    application.run_polling()


if __name__ == "__main__":
    print("Bot is starting...")
    main()
