# ---------------- TElEGRAM BOT -------------------

from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackContext, filters
import logging
import json

TOKEN = "7903410355:AAFc88HhZtqvfZ3rGzKRCZUJMUwVZFaWiqU"
LOG_FILE = "conversations.log"

try: 
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        user_conversations = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    user_conversations = {}


async def store_message(user_id: str, user_name: str, user_message: str, bot_message: str, timestamp: str, user_conversations: dict, log_file: str):
    user_key = f"{user_name}_{user_id}"

    if user_key not in user_conversations:
        user_conversations[user_key] = {"total_sessions_logged": 0, "conversation_stream": []}  # Create a new conversation dictionary for the user if it doesn't exist   
  
    user_conversations[user_key]["conversation_stream"].append({"User": user_message, "Timestamp": timestamp})  # user message
    user_conversations[user_key]["conversation_stream"].append({"Bot": bot_message}) # bot message

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(user_conversations, f, indent=4, ensure_ascii=False)  



async def generate_bot_message(user_id: str, user_name: str, user_message: str, user_conversations: dict) -> str:
    user_key = f"{user_name}_{user_id}"

    if user_key not in user_conversations:
        user_conversations[user_key] = {"total_sessions_logged": 0, "conversation_stream": []}  # Create a new conversation dictionary for the user if it doesn't exist   
  
    if user_message.upper() == "GYM":
        user_conversations[user_key]["total_sessions_logged"] += 1
        session_count = user_conversations[user_key]["total_sessions_logged"]
        return f"You have successfully logged a gym session! 🤸\n\nNumber of gym sessions logged: {session_count}"
    else:
        return "send GYM to log a gym session"




async def handle_message(update: Update, context: CallbackContext) -> None:
    global user_conversations

    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.username
    user_message = update.message.text.strip()
    timestamp = str(update.message.date)

    bot_message = await generate_bot_message(user_id, user_name, user_message, user_conversations)
    await store_message(user_id, user_name, user_message, bot_message, timestamp, user_conversations, LOG_FILE)
    
    await update.message.reply_text(bot_message)





def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) # Add a message handler to check incoming text
    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()



## json file structure

converstions = { #dict  -- each key is a unique user
    "User_123": { #dict -- each key contains details about the conversation (variables)
        "total_sessions_logged" : 0,
        "total_sessions_logged_this_week": 2,
        "conversation_stream": [ #list of dictionaries
            {"User": "Hello", "Timestamp": "2021-09-15 12:00:00"}, # each dictionary is a message, values are details about the message
            {"Bot": "Hi there!"}
        ]
    }
}
