import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
API_KEY = "bara"
BASE_URL = "https://hl-hadi.info.gf/cmsg/api.php"
BOT_TOKEN = "8206814818:AAFjR0I1iyWedDf9pIVP8kkrR0rXnIoD-Mw"
ADMIN_ID = 6556220592  # Change this to your Telegram user ID

# --- Command: /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the SMS Bot!\nUse /send <number> <message> to send SMS.")

# --- Command: /send <number> <message> ---
async def send_sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /send <number> <message>")
        return

    number = context.args[0]
    message = " ".join(context.args[1:])

    url = f"{BASE_URL}?key={API_KEY}&number={number}&msg={message}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            await update.message.reply_text(f"✅ SMS sent to {number}!")
        else:
            await update.message.reply_text(f"❌ Failed to send SMS. API error.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

# --- Main Function ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_sms))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
