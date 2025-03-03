# to message user manually 

import requests
from texts.telegram_sensitive_info import TOKEN
from texts.telegram_sensitive_info import LOG_FILE

BOT_TOKEN = TOKEN
CHAT_ID = ""
MESSAGE = ""

chat_id_input = input("Input user's chat id: ")
CHAT_ID = chat_id_input

message_input = input("Insert the message you would like to send to a user: ")
MESSAGE = input

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
params = {"chat_id": CHAT_ID, "text": MESSAGE}

response = requests.get(url, params=params)
print(response.json())