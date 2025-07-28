from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
import httpx
from filter import load_bad_words, contains_bad_word

# === CONFIG ===
BOT_TOKEN = "8206814818:AAFjR0I1iyWedDf9pIVP8kkrR0rXnIoD-Mw"
API_KEY = "parvej"
BASE_URL = "https://hl-hadi.info.gf/cmsg/api.php"

# === STATES ===
ASK_NUMBER, ASK_MESSAGE = range(2)

# Load bad words once
bad_words = load_bad_words()

# === START COMMAND ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📤 Send SMS"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Welcome! Click below to send an SMS.", reply_markup=reply_markup)

# === ASK FOR PHONE NUMBER ===
async def ask_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📱 Enter the phone number:")
    return ASK_NUMBER

# === GET PHONE NUMBER ===
async def get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['number'] = update.message.text
    await update.message.reply_text("💬 Now enter the message:")
    return ASK_MESSAGE

# === GET MESSAGE AND SEND SMS WITH FILTER ===
async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = context.user_data.get('number')
    message = update.message.text

    # Check for bad words
    if contains_bad_word(message, bad_words):
        await update.message.reply_text("অভদ্র ছেলে তোমার মেসেজ সেন্ড করা যাবে না। খারাপ ভাষা ইউজ করছো 😤")
        return ConversationHandler.END

    # Prepare params for API call
    params = {
        "key": API_KEY,
        "number": number,
        "msg": message
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(BASE_URL, params=params)
        if res.status_code == 200:
            await update.message.reply_text(f"✅ SMS sent to {number}!")
        else:
            await update.message.reply_text("❌ Failed to send SMS.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

    return ConversationHandler.END

# === CANCEL HANDLER ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation canceled.")
    return ConversationHandler.END

# === MAIN FUNCTION ===
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
