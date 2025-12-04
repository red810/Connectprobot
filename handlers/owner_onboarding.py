"""
owner_onboarding.py
Handles:
- Shared Bot setup (no subscription)
- Mini Bot setup (trial + future subscription)
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db, Owner
from sqlalchemy.future import select
from datetime import datetime, timedelta

# --- Shared Bot Flow (No Subscription Required) ---

async def shared_bot_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["setup_type"] = "shared"
    await query.edit_message_text("📝 Enter your **Business or Channel Name**:")
    return "ASK_NAME"


async def save_business_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["business_name"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("Tech", callback_data="cat_Tech"),
         InlineKeyboardButton("Education", callback_data="cat_Education")],
        [InlineKeyboardButton("E-commerce", callback_data="cat_Ecommerce"),
         InlineKeyboardButton("Other", callback_data="cat_Other")]
    ]
    
    await update.message.reply_text(
        "📂 Choose your **Category**", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return "ASK_CATEGORY"


async def save_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("cat_", "")
    context.user_data["category"] = category

    await query.edit_message_text("✍ Add a short **Bio / Description**:")
    return "ASK_BIO"


async def save_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["bio"] = update.message.text
    await update.message.reply_text("📸 Upload Logo (optional) or type **Skip**")
    return "ASK_LOGO"


async def save_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logo = None

    if update.message.photo:
        logo = update.message.photo[-1].file_id

    # Save Database
    async for db in get_db():
        owner = Owner(
            telegram_id=str(update.effective_user.id),
            business_name=context.user_data["business_name"],
            category=context.user_data["category"],
            bio=context.user_data["bio"],
            logo_file_id=logo,
            subscription_plan="free_shared",
            trial_ends=None,
            subscribed=False
        )
        db.add(owner)
        await db.commit()

    await update.message.reply_text(
        "🎉 **Your Profile is Ready!**\n"
        "You can now receive messages and reply privately.\n\n"
        "**Plan:** Free Shared Bot (No Subscription Required)"
    )