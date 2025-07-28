from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
import requests

# === CONFIG ===
BOT_TOKEN = "8206814818:AAFjR0I1iyWedDf9pIVP8kkrR0rXnIoD-Mw"
API_KEY = "bara"
BASE_URL = "https://hl-hadi.info.gf/cmsg/api.php"

# === STATE ===
ASK_NUMBER, ASK_MESSAGE = range(2)

# === START ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📤 Send SMS"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Welcome! Click below to send an SMS.", reply_markup=reply_markup)

# === HANDLE "Send SMS" button ===
async def ask_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📱 Enter the phone number:")
    return ASK_NUMBER

# === Get Number ===
async def get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['number'] = update.message.text
    await update.message.reply_text("💬 Now enter the message:")
    return ASK_MESSAGE

# === Get Message and Send SMS ===
async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = context.user_data['number']
    message = update.message.text
    url = f"{BASE_URL}?key={API_KEY}&number={number}&msg={message}"
    
    try:
        res = requests.get(url)
        if res.status_code == 200:
            await update.message.reply_text(f"✅ SMS sent to {number}!")
        else:
            await update.message.reply_text("❌ Failed to send SMS.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")
    
    return ConversationHandler.END

# === CANCEL ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Canceled.")
    return ConversationHandler.END

# === MAIN ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📤 Send SMS$"), ask_number)
        ],
        states={
            ASK_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_number)],
            ASK_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
