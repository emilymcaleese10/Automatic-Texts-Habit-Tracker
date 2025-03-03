# ---------------- TElEGRAM BOT -------------------

from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackContext, filters
import json, time, asyncio
from datetime import datetime

from texts.telegram_sensitive_info import TOKEN, LOG_FILE
from texts.location_functions import calculate_distance, TRINITY_LAT, TRINITY_LON, RADIUS_METERS

from rewards.edit_rewards_sheet import get_and_update_n
from rewards.gspread_sensitive_info import authenticate_google_sheets, JSON_KEYFILE, SHEET_URL

from data_handling.constants import ELAPSED_TIME_FOR_NEXT_LOG
from data_handling.time_elapse_functions import ready_to_update_counter, reset_all_variables
from data_handling.update_ticks import update_weekly_progress

client = authenticate_google_sheets(JSON_KEYFILE)

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


async def generate_bot_message(user_key: str, user_id: str, user_name: str, user_location, user_conversations: dict) -> str:
    """ Generate a response based on user input and logs progress"""
    # return location_handler 
    current_time = time.time()
    ready_to_log = await ready_to_update_counter(user_key, user_conversations)
    next_log_time = current_time + ELAPSED_TIME_FOR_NEXT_LOG
    formatted_time = datetime.fromtimestamp(next_log_time).strftime('%H:%M %Y/%m/%d')

    if not user_location:
        return "Send your live location (at Trinity Gym) to log a gym session."
    
    user_lat, user_lon = user_location.latitude, user_location.longitude
    distance = calculate_distance(user_lat, user_lon, TRINITY_LAT, TRINITY_LON)

    if distance > RADIUS_METERS:
        return f"❌ You are {int(distance)} meters away from Trinity Gym. Move closer to log a session."

    logs_until_reward = user_conversations[user_key]["logs_until_reward"]

    if not ready_to_log:
        return f"You have only recently logged a gym session. 🏋\n\nNext time you can log a session is: \n{formatted_time}."

    user_conversations[user_key]["total_sessions_logged"] += 1
    user_conversations[user_key]["logs_until_reward"] = max(0, logs_until_reward - 1)
    user_conversations[user_key]["last_log_time"] = current_time

    total_session_count = user_conversations[user_key]["total_sessions_logged"]
    logs_until_reward = user_conversations[user_key]["logs_until_reward"]
    weekly_progress_ticks = update_weekly_progress(user_key, user_conversations)

    if logs_until_reward == 0 and not user_conversations[user_key]["goal_achieved"]:
        reward_code = get_and_update_n(client, SHEET_URL)
        user_conversations[user_key]["goal_achieved"] = True
        return (f"You have successfully achieved your week's goal! 🥳\n\n"
        f"Give the code below to the gym receptionist to receive your reward.\n\n"
        f"Code: {reward_code}")
    
    return (f"You have successfully logged a gym session! 🤸\n\n"
        f"{weekly_progress_ticks}\n\n"
        f"Total number of gym sessions logged: {total_session_count}\n\n"
        f"Sessions left to log this week before reward: {logs_until_reward}")


async def handle_message(update: Update, context: CallbackContext) -> None:
    global user_conversations

    if not update.message:
        return

    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.username
    timestamp = str(update.message.date)
    user_key = f"{user_name}_{user_id}"

    if user_key not in user_conversations:
        user_conversations[user_key] = {
            "total_sessions_logged": 0, 
            "weekly_log_goal": 2, 
            "logs_until_reward": 2, 
            "last_log_time": time.time(), 
            "goal_achieved": False, 
            "weekly_progress": {}, 
            "conversation_stream": []
        }  # Create a new conversation dictionary for the user if it doesn't exist   

    user_location = update.message.location

    if user_location and not user_location.live_period:
        await update.message.reply_text("❌ Please share your LIVE location instead of selecting a location on the map.")
        return

    bot_message = await generate_bot_message(user_key, user_id, user_name, user_location, user_conversations)

    await store_message(user_key, user_id, user_name, "Sent Live Location" if user_location else "No Location", bot_message, timestamp, user_conversations, LOG_FILE)
    await update.message.reply_text(bot_message)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, lambda update, context: handle_message(update, context))) # Add a message handler to check incoming text
    
    loop = asyncio.get_event_loop()
    loop.create_task(reset_all_variables(user_conversations))  # USING USER_CONVERSATIONS
    

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
