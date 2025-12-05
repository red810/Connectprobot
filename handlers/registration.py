"""
registration.py
Handles:
- New user start
- Shows Register button
- Detects owner or normal user
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db, Owner
from config import settings
from sqlalchemy.future import select
from datetime import datetime, timedelta

INTRO_MESSAGE = """
👋 Welcome to ConnectProBot!

Through this bot, you can safely connect and message Telegram channel or business owners.

💼 How it works:
1️⃣ If you came here via a channel link, your messages go directly to that owner.
2️⃣ The owner can reply to you privately — without sharing any personal info.

🔒 Privacy Protected | ⚡ Fast Replies  
🤖 Powered by ConnectProBot — Connecting Creators with Their Audience!
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Register", callback_data="register_owner")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(INTRO_MESSAGE, reply_markup=reply_markup)


async def register_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Inline Options
    keyboard = [
        [
            InlineKeyboardButton("Start With this Bot", callback_data="shared_bot"),
            InlineKeyboardButton("Start Your Own Bot", callback_data="mini_bot"),
        ]
    ]

    await query.edit_message_text(
        "**Select how you want to use ConnectProBot:**",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )