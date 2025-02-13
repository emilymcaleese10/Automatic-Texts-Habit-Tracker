# ---------------- TElEGRAM BOT -------------------

from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackContext, filters
import json
import time
from datetime import datetime

TOKEN = "7903410355:AAFc88HhZtqvfZ3rGzKRCZUJMUwVZFaWiqU"
LOG_FILE = "conversations.log"
ELAPSED_TIME_FOR_NEXT_LOG = 6*3600 # 6 hours in seconds

try: 
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        user_conversations = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    user_conversations = {}


async def store_message(user_key: str, user_id: str, user_name: str, user_message: str, bot_message: str, timestamp: str, user_conversations: dict, log_file: str):

    user_conversations[user_key]["conversation_stream"].append({"User": user_message, "Timestamp": timestamp})  # user message
    user_conversations[user_key]["conversation_stream"].append({"Bot": bot_message}) # bot message

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(user_conversations, f, indent=4, ensure_ascii=False)  


async def ready_to_update_counter(user_key: str) -> bool:
    if user_conversations[user_key]["total_sessions_logged"] == 0:
        return True
    
    # return true if 6 hours have passed since last log 
    current_time = time.time()
    last_log_time = user_conversations[user_key]["last_log_time"]
    return (current_time - last_log_time >= 20) # CHANGE TO ELAPSED_TIME_FOR_NEXT_LOG



async def generate_bot_message(user_key: str, user_id: str, user_name: str, user_message: str, user_conversations: dict) -> str:
    current_time = time.time()

    ready_to_log = await ready_to_update_counter(user_key)

    six_hours_later = current_time + ELAPSED_TIME_FOR_NEXT_LOG

    # Convert to a human-readable format
    formatted_time = datetime.fromtimestamp(six_hours_later).strftime('%H:%M %Y/%m/%d')

    if user_message.upper() == "GYM":
        if ready_to_log:       
            user_conversations[user_key]["total_sessions_logged"] += 1
            total_session_count = user_conversations[user_key]["total_sessions_logged"]

            user_conversations[user_key]["logs_until_reward"] -= 1
            logs_until_reward = user_conversations[user_key]["logs_until_reward"]

            user_conversations[user_key]["last_log_time"] = current_time
            return f"You have successfully logged a gym session! 🤸\n\nTotal number of gym sessions logged: {total_session_count}\n\nSessions left to log this week before reward: {logs_until_reward}"
        else: 
            return f"You have recently logged a gym session. \nNext time you can log a session is: \n{formatted_time}."
    else:
        return "send GYM to log a gym session"
    

async def handle_message(update: Update, context: CallbackContext) -> None:
    global user_conversations

    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.username
    user_message = update.message.text.strip()
    timestamp = str(update.message.date)

    user_key = f"{user_name}_{user_id}"

    if user_key not in user_conversations:
        user_conversations[user_key] = {"total_sessions_logged": 0, "weekly_log_goal": 2, "logs_until_reward": 2, "last_log_time": time.time(), "conversation_stream": []}  # Create a new conversation dictionary for the user if it doesn't exist   

    bot_message = await generate_bot_message(user_key, user_id, user_name, user_message, user_conversations)
    await store_message(user_key, user_id, user_name, user_message, bot_message, timestamp, user_conversations, LOG_FILE)
    
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
