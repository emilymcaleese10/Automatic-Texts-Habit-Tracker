# ---------------- TElEGRAM BOT -------------------

from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackContext, filters

TOKEN = "7903410355:AAFc88HhZtqvfZ3rGzKRCZUJMUwVZFaWiqU"

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.strip().upper() 
    if user_message == "GYM":
        await update.message.reply_text("You have logged a gym session!")
    # else:
    #     await update.message.reply_text("Send 'GYM' to log your session.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) # Add a message handler to check incoming text
    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()