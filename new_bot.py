from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
import requests
import time

BOT_TOKEN = "8076211324:AAFtJDD6FXh1f3iIAstYFOjlJYu81REdW0E"

USERS = {}
ADMINS = [6556220592]  # Replace with your Telegram user ID
BAD_WORDS = ["fuck", "shit", "chuda", "gandu", "madarchod", "bokachoda"]

SMS_NUMBER, SMS_MESSAGE = range(2)

def is_admin(user_id):
    return user_id in ADMINS

def is_muted(user_id):
    return time.time() < USERS.get(user_id, {}).get("muted_until", 0)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in USERS:
        USERS[user.id] = {"name": user.first_name, "coin": 0, "permission": False, "muted_until": 0}
    await update.message.reply_text(f"👋 Welcome {user.first_name}!\n🤖 This is *SM×JB* Bot.\nUse /insight to see your commands.")

async def insight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 Your Commands:\n"
        "/start - Start the bot\n"
        "/sms - Send SMS (if allowed)\n"
        "/balance - Show your coin balance"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    coin = USERS.get(uid, {}).get("coin", 0)
    await update.message.reply_text(f"💰 You have {coin} coin(s).")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text = "📊 All Users Info:\n\n"
    for uid, data in USERS.items():
        text += f"🧑‍💻 ID: {uid}, Name: {data['name']}, Coin: {data['coin']}, Perm: {data['permission']}\n"
    await update.message.reply_text(text)

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        uid = int(context.args[0])
        USERS[uid]["permission"] = True
        await update.message.reply_text("✅ Permission granted.")
    except:
        await update.message.reply_text("❌ Usage: /add <user_id>")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        uid = int(context.args[0])
        USERS[uid]["permission"] = False
        await update.message.reply_text("❌ Permission revoked.")
    except:
        await update.message.reply_text("❌ Usage: /remove <user_id>")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        uid = int(context.args[0])
        hours = int(context.args[1])
        USERS[uid]["muted_until"] = time.time() + hours * 3600
        await update.message.reply_text("🔇 User muted.")
    except:
        await update.message.reply_text("❌ Usage: /mute <user_id> <hours>")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        uid = int(context.args[0])
        USERS[uid]["muted_until"] = 0
        await update.message.reply_text("🔊 User unmuted.")
    except:
        await update.message.reply_text("❌ Usage: /unmute <user_id>")

async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        uid = int(context.args[0])
        amount = int(context.args[1])
        USERS[uid]["coin"] = amount
        await update.message.reply_text("💰 Coin updated.")
    except:
        await update.message.reply_text("❌ Usage: /coin <user_id> <amount>")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 Available Commands:\n\n"
        "1. /start - Start the bot\n"
        "2. /sms - Send an SMS (requires permission and 1 coin)\n"
        "3. /info - View all users' info (Admin)\n"
        "4. /add <user_id> - Grant SMS permission (Admin)\n"
        "5. /remove <user_id> - Revoke SMS permission (Admin)\n"
        "6. /mute <user_id> <hours> - Mute a user (Admin)\n"
        "7. /unmute <user_id> - Unmute a user (Admin)\n"
        "8. /coin <user_id> <amount> - Set coins for a user (Admin)\n"
        "9. /balance - Check your coin balance\n"
        "10. /view - View sent messages (Admin)\n"
        "11. /help - Show this help (Admin)\n"
        "12. /insight - Show user commands\n"
        "13. /cancel - Cancel current operation"
    )

# SMS SEND FLOW:
async def sms_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = USERS.get(uid)

    if not user or not user.get("permission"):
        return await update.message.reply_text("⛔ You don't have permission to send SMS.")
    if user["coin"] < 1:
        return await update.message.reply_text("💸 You need at least 1 coin.")
    if is_muted(uid):
        return await update.message.reply_text("❌ You are muted.")

    await update.message.reply_text("📲 Send recipient phone number:")
    return SMS_NUMBER

async def sms_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["number"] = update.message.text
    await update.message.reply_text("💬 Now send the message:")
    return SMS_MESSAGE

async def sms_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    message_text = update.message.text

    if any(bad in message_text.lower() for bad in BAD_WORDS):
        return await update.message.reply_text("🚫 Blocked: offensive language detected.")

    number = context.user_data["number"]
    url = f"https://hl-hadi.info.gf/cmsg/api.php?key=bara&number={number}&msg={message_text}"

    res = requests.get(url)
    if "success" in res.text.lower():
        USERS[uid]["coin"] -= 1
        await update.message.reply_text("✅ SMS sent. 1 coin deducted.")
    else:
        await update.message.reply_text("❌ Failed to send SMS.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END

# Run Bot
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("coin", coin))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("insight", insight))

    sms_conv = ConversationHandler(
        entry_points=[CommandHandler("sms", sms_start)],
        states={
            SMS_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, sms_number)],
            SMS_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sms_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(sms_conv)

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
