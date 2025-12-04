"""
ConnectsProBot — Main Application File
"""

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

import os
from dotenv import load_dotenv
import sys

# Load env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Validate values
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN is missing in .env file!")
    sys.exit()

if not ADMIN_ID:
    print("❌ ERROR: ADMIN_ID is missing in .env file!")
    sys.exit()

try:
    ADMIN_ID = int(ADMIN_ID)
except ValueError:
    print("❌ ERROR: ADMIN_ID must be a NUMBER (your Telegram user ID).")
    sys.exit()

# --- HANDLER IMPORTS ---
from handlers.menu import main_menu, about_page, settings_page
from handlers.messaging import user_message_handler, reply_button_handler, send_owner_reply
from handlers.security import anti_spam
from handlers.export import export_json
from handlers.lang import language_menu
from handlers.trialstop import trial_active

# JOBS (cleanup + trial)
from jobs.cleanup import delete_old_messages
from jobs.trialchecker import check_trial


async def message_router(update, context):
    user_id = update.effective_user.id

    if not anti_spam(user_id):
        await update.message.reply_text("🚫 Slow down — Please wait 3 seconds.")
        return

    await delete_old_messages()
    await check_trial(BOT_TOKEN)
    await user_message_handler(update, context)


async def owner_reply_router(update, context):
    owner_id = update.effective_user.id

    if not trial_active(owner_id):
        await update.message.reply_text("⛔ Trial expired — upgrade required.")
        return

    await send_owner_reply(update, context)


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", main_menu))
    application.add_handler(CommandHandler("export", export_json))
    application.add_handler(CommandHandler("language", language_menu))

    # Buttons
    application.add_handler(CallbackQueryHandler(main_menu, pattern="back_menu"))
    application.add_handler(CallbackQueryHandler(about_page, pattern="about"))
    application.add_handler(CallbackQueryHandler(settings_page, pattern="settings"))
    application.add_handler(CallbackQueryHandler(reply_button_handler, pattern="reply_"))

    # Message Routing
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))
    application.add_handler(MessageHandler(filters.REPLY & filters.TEXT, owner_reply_router))

    application.run_polling()


if __name__ == "__main__":
    main()