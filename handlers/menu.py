"""
menu.py
Handles:
- Main Menu UI
- About Page
- Settings Button (future gateway)
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import settings


def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("💬 Message Admin", callback_data="msg_admin")],
        [InlineKeyboardButton("ℹ About Us", callback_data="about")],
        [InlineKeyboardButton("⚙ Settings", callback_data="settings")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user = query.message.chat
        await query.edit_message_text(
            f"👋 **Hello {user.first_name}!**\nWelcome to your bot!",
            reply_markup=main_menu_keyboard()
        )
    else:
        user = update.message.chat
        await update.message.reply_text(
            f"👋 **Hello {user.first_name}!**\nWelcome to your bot!",
            reply_markup=main_menu_keyboard()
        )


async def about_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        f"📌 **About This Bot**\n\n"
        f"This bot helps you manage your leads and respond quickly.\n"
        f"💡 Auto reply system\n"
        f"💡 Admin direct inbox system\n"
        f"💡 Free Trial: {settings.TRIAL_MONTHS} Months\n\n"
        f"Powered by ConnectsProBot Platform\n"
        f"This Bot was made using @Connectsprobot"
    )

    await query.edit_message_text(text, reply_markup=main_menu_keyboard())


async def settings_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🌐 Add Payment Gateway (Coming Soon)", callback_data="none")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]
    ]

    await query.edit_message_text(
        "⚙ **Settings & Controls**\n\n"
        "Here you will control:\n"
        "✔ Payments\n"
        "✔ Subscription Upgrade\n"
        "✔ Bot Customization\n\n"
        "This Bot was made using @Connectsprobot",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )