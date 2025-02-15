# to message user manually 

import requests

BOT_TOKEN = ""
CHAT_ID = ""
MESSAGE = ""

token_input = input("Insert the bot token you would like to user: ")
BOT_TOKEN = token_input

chat_id_input = input("Input user's chat id: ")
CHAT_ID = chat_id_input

message_input = input("Insert the message you would like to send to a user: ")
MESSAGE = input

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
params = {"chat_id": CHAT_ID, "text": MESSAGE}

response = requests.get(url, params=params)
print(response.json())