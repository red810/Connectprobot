"""
Main entrypoint that wires everything together.
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from handlers.registration import (
    start_owner_onboarding,
    owner_callback_query_handler,
    owner_message_flow,
    owner_logo_handler,
    plan_selected_callback,
    payment_method_selected
)
from handlers.dashboard import dashboard_command, dashboard_callback
from handlers.admin import admin_panel_cmd
from handlers.messages import start_for_user, direct_message_to_owner
from database import init_db

BOT_TOKEN = os.getenv('BOT_TOKEN')


def main():
    """Main function to run the bot."""
    # Initialize DB first (sync wrapper for async init)
    asyncio.get_event_loop().run_until_complete(init_db())

    # Build application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # General handlers
    app.add_handler(CommandHandler('start', direct_message_to_owner))
    app.add_handler(CommandHandler('dashboard', dashboard_command))
    app.add_handler(CommandHandler('admin', admin_panel_cmd))

    # Owner onboarding
    app.add_handler(CommandHandler('owner', start_owner_onboarding))
    app.add_handler(CallbackQueryHandler(owner_callback_query_handler, pattern='^(start_own|manage_existing)$'))
    
    # Message handlers for onboarding flow
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, owner_message_flow))
    app.add_handler(MessageHandler(filters.PHOTO, owner_logo_handler))
    
    # Plan and payment callbacks
    app.add_handler(CallbackQueryHandler(plan_selected_callback, pattern='^plan_'))
    app.add_handler(CallbackQueryHandler(payment_method_selected, pattern='^pay_'))

    # Dashboard callbacks
    app.add_handler(CallbackQueryHandler(dashboard_callback, pattern='^dash_'))

    # Start the bot with polling
    print('Starting ConnectProBot...')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
