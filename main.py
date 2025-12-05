"""
ConnectsProBot — Main Application
"""
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import settings
from database import init_db
from handlers.menu import main_menu, about_page, settings_page
from handlers.messaging import user_message_handler, reply_button_handler, send_owner_reply
from handlers.security import anti_spam
from handlers.export import export_json
from handlers.lang import language_menu
from handlers.trialstop import trial_active
from jobs.cleanup import delete_old_messages
from jobs.trialchecker import check_trial

async def post_init(application):
    await init_db(settings.DATABASE_URL)

async def message_router(update, context):
    user_id = update.effective_user.id
    if not anti_spam(user_id):
        await update.message.reply_text("🚫 Slow down — Please wait 4 seconds.")
        return
    await user_message_handler(update, context)

async def owner_reply_router(update, context):
    owner_id = update.effective_user.id
    if not await trial_active(owner_id):
        await update.message.reply_text("⛔ Trial expired — upgrade required.")
        return
    await send_owner_reply(update, context)

def main():
    application = ApplicationBuilder().token(settings.BOT_TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", main_menu))
    application.add_handler(CommandHandler("export", export_json))
    application.add_handler(CommandHandler("language", language_menu))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="back_menu"))
    application.add_handler(CallbackQueryHandler(about_page, pattern="about"))
    application.add_handler(CallbackQueryHandler(settings_page, pattern="settings"))
    application.add_handler(CallbackQueryHandler(reply_button_handler, pattern="reply_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.REPLY, message_router))
    application.add_handler(MessageHandler(filters.REPLY & filters.TEXT, owner_reply_router))
    
    application.run_polling()

if __name__ == "__main__":
    main()
    