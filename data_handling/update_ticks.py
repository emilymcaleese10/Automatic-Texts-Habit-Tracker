from datetime import datetime

from data_handling.constants import RESET_INTERVAL, DAYS_OF_THE_WEEK_DICT
from texts.telegram_sensitive_info import LOG_FILE

def update_progress_ticks(user_key: str, user_conversations: dict) -> str:
    """Updates and returns the weekly progress string with green and gray ticks."""

    # Initialize user's weekly progress to grey ticks
    if user_conversations[user_key]["progress_ticks"] == {}:
        user_conversations[user_key]["progress_ticks"] = DAYS_OF_THE_WEEK_DICT.copy()

    today = datetime.today().strftime("%A")
    user_conversations[user_key]["progress_ticks"][today] = "✅"

    progress_message = "Weekly Progress:\n" + "\n".join(
        [f"{user_conversations[user_key]['progress_ticks'][day]} {day}" for day in DAYS_OF_THE_WEEK_DICT]
    )

    return progress_message