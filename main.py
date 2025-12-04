"""
main.py
ConnectsProBot — Main Application
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

# Load ENV
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# HANDLERS
from handlers.menu import main_menu, about_page, settings_page
from handlers.messaging import user_message_handler, reply_button_handler, send_owner_reply
from handlers.security import anti_spam
from handlers.export import export_json
from handlers.lang import language_menu
from handlers.trialstop import trial_active

# JOBS
from jobs.cleanup import delete_old_messages
from jobs.trialchecker import check_trial


async def message_router(update, context):
    user_id = update.effective_user.id

    # Anti-Spam Check
    if not anti_spam(user_id):
        await update.message.reply_text("🚫 Slow down — Please wait 3 seconds.")
        return

    # Background Jobs
    await delete_old_messages()
    await check_trial(BOT_TOKEN)

    # Process User Message
    await user_message_handler(update, context)



async def owner_reply_router(update, context):
    """
    Only allows ADMIN to reply to forwarded messages
    """
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not trial_active(ADMIN_ID):
        await update.message.reply_text("⛔ Trial expired — upgrade required.")
        return
    
    # If admin replies to a bot-forwarded message
    if update.message.reply_to_message:
        await send_owner_reply(update, context)



def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # START
    application.add_handler(CommandHandler("start", main_menu))

    # CALLBACK BUTTON PAGES
    application.add_handler(CallbackQueryHandler(main_menu, pattern="back_menu"))
    application.add_handler(CallbackQueryHandler(about_page, pattern="about"))
    application.add_handler(CallbackQueryHandler(settings_page, pattern="settings"))
    application.add_handler(CallbackQueryHandler(reply_button_handler, pattern="reply_"))

    # EXPORT
    application.add_handler(CommandHandler("export", export_json))
    application.add_handler(CommandHandler("language", language_menu))

    # USER MESSAGE HANDLER
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))

    # ONLY OWNER REPLY HANDLER
    application.add_handler(
        MessageHandler(filters.REPLY & filters.TEXT, owner_reply_router)
    )

    application.run_polling()


if __name__ == "__main__":
    main()