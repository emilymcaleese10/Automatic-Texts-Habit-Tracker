import asyncio
import json
from datetime import datetime
import time

from data_handling.constants import RESET_INTERVAL, DAYS_OF_THE_WEEK_DICT, ELAPSED_TIME_FOR_NEXT_LOG
from texts.telegram_sensitive_info import LOG_FILE


async def reset_all_variables(user_conversations):
    """Resets logs_until_reward every 45 seconds."""

    # TODO change so that it resets on monday not every 7 days 
    while True:
        await asyncio.sleep(RESET_INTERVAL)  # Wait

        for user_key in user_conversations:
            user_conversations[user_key]["logs_until_reward"] = user_conversations[user_key]["weekly_log_goal"] # reset logs_until_reward
            user_conversations[user_key]["goal_achieved"] = False
            user_conversations[user_key]["weekly_progress"] = DAYS_OF_THE_WEEK_DICT.copy() # reset ticks
            user_conversations[user_key]["reward_received"] = False

        # Save changes to file
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(user_conversations, f, indent=4, ensure_ascii=False)
        
        print(f"✅ logs_until_reward reset for all users. {datetime.fromtimestamp(time.time()).strftime('%H:%M %Y/%m/%d')}")



async def ready_to_update_counter(user_key: str, user_conversations) -> bool:
    if user_conversations[user_key]["total_sessions_logged"] == 0:
        return True
    
    # return true if 6 hours have passed since last log 
    current_time = time.time()
    last_log_time = user_conversations[user_key]["last_log_time"]
    return (current_time - last_log_time >= ELAPSED_TIME_FOR_NEXT_LOG)