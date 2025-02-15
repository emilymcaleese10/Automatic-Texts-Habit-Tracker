# ---------------- TElEGRAM BOT -------------------

from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackContext, filters
import json
import time
from datetime import datetime
import asyncio
from telegram_sensitive_info import TOKEN
from telegram_sensitive_info import LOG_FILE

ELAPSED_TIME_FOR_NEXT_LOG = 6*3600 # 6 hours in seconds
RESET_INTERVAL = 45 # 45 seconds
DAYS_OF_THE_WEEK_DICT = {
    "Monday": "☑",
    "Tuesday": "☑",
    "Wednesday": "☑",
    "Thursday": "☑",
    "Friday": "☑",
    "Saturday": "☑",
    "Sunday": "☑"
}

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


def update_weekly_progress(user_key: str, user_conversations: dict) -> str:
    """Updates and returns the weekly progress string with green and gray ticks."""

    current_days_of_the_week = {
        "Monday": "☑",
        "Tuesday": "☑",
        "Wednesday": "☑",
        "Thursday": "☑",
        "Friday": "☑",
        "Saturday": "☑",
        "Sunday": "☑"
}

    # Initialize user's weekly progress to grey ticks
    if user_conversations[user_key]["weekly_progress"] == {}:
        user_conversations[user_key]["weekly_progress"] = DAYS_OF_THE_WEEK_DICT.copy()

    today = datetime.today().strftime("%A")
    user_conversations[user_key]["weekly_progress"][today] = "✅"

    progress_message = "Weekly Progress:\n" + "\n".join(
        [f"{user_conversations[user_key]['weekly_progress'][day]} {day}" for day in DAYS_OF_THE_WEEK_DICT]
    )

    return progress_message



async def generate_bot_message(user_key: str, user_id: str, user_name: str, user_message: str, user_conversations: dict) -> str:
    current_time = time.time()
    ready_to_log = await ready_to_update_counter(user_key)

    six_hours_later = current_time + ELAPSED_TIME_FOR_NEXT_LOG
    formatted_time = datetime.fromtimestamp(six_hours_later).strftime('%H:%M %Y/%m/%d')

    if user_message.upper() == "GYM":
        if ready_to_log:       
            user_conversations[user_key]["total_sessions_logged"] += 1
            total_session_count = user_conversations[user_key]["total_sessions_logged"]
            
            if user_conversations[user_key]["logs_until_reward"] > 0: # prevents minus numbers
                user_conversations[user_key]["logs_until_reward"] -= 1
            logs_until_reward = user_conversations[user_key]["logs_until_reward"]

            weekly_progress_ticks = update_weekly_progress(user_key, user_conversations)

            user_conversations[user_key]["last_log_time"] = current_time 
            bot_response = f"You have successfully logged a gym session! 🤸\n\n{weekly_progress_ticks}\n\nTotal number of gym sessions logged: {total_session_count}\n\nSessions left to log this week before reward: {logs_until_reward}"
        else: 
            bot_response = f"You have only recently logged a gym session. 🏋\n\nNext time you can log a session is: \n{formatted_time}."
        return bot_response
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
        user_conversations[user_key] = {"total_sessions_logged": 0, "weekly_log_goal": 2, "logs_until_reward": 2, "last_log_time": time.time(), "weekly_progress": {}, "conversation_stream": []}  # Create a new conversation dictionary for the user if it doesn't exist   

    bot_message = await generate_bot_message(user_key, user_id, user_name, user_message, user_conversations)
    await store_message(user_key, user_id, user_name, user_message, bot_message, timestamp, user_conversations, LOG_FILE)
    
    await update.message.reply_text(bot_message)


async def reset_all_variables():
    """Resets logs_until_reward every 45 seconds."""
    global user_conversations

    while True:
        await asyncio.sleep(RESET_INTERVAL)  # Wait

        for user_key in user_conversations:
            user_conversations[user_key]["logs_until_reward"] = user_conversations[user_key]["weekly_log_goal"] # reset logs_until_reward
        
        user_conversations[user_key]["weekly_progress"] = DAYS_OF_THE_WEEK_DICT.copy() # reset ticks

        # Save changes to file
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(user_conversations, f, indent=4, ensure_ascii=False)
        
        print(f"✅ logs_until_reward reset for all users. {datetime.fromtimestamp(time.time()).strftime('%H:%M %Y/%m/%d')}")



def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) # Add a message handler to check incoming text
    
    loop = asyncio.get_event_loop()
    loop.create_task(reset_all_variables())

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
