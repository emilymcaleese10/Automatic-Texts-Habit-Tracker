from datetime import datetime

from data_handling.constants import RESET_INTERVAL, DAYS_OF_THE_WEEK_DICT
from texts.telegram_sensitive_info import LOG_FILE

def update_weekly_progress(user_key: str, user_conversations: dict) -> str:
    """Updates and returns the weekly progress string with green and gray ticks."""

    # Initialize user's weekly progress to grey ticks
    if user_conversations[user_key]["weekly_progress"] == {}:
        user_conversations[user_key]["weekly_progress"] = DAYS_OF_THE_WEEK_DICT.copy()

    today = datetime.today().strftime("%A")
    user_conversations[user_key]["weekly_progress"][today] = "✅"

    progress_message = "Weekly Progress:\n" + "\n".join(
        [f"{user_conversations[user_key]['weekly_progress'][day]} {day}" for day in DAYS_OF_THE_WEEK_DICT]
    )

    return progress_message