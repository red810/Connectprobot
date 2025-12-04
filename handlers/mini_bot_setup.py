"""
mini_bot_setup.py
Handles:
- Full mini bot onboarding
- Bot token validation
- 4-Month Free Trial
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from database import get_db, Owner
from sqlalchemy.future import select
import aiohttp
from config import settings


async def start_mini_bot_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["setup_type"] = "mini"
    await query.edit_message_text("📝 Enter your **Business or Channel Name**:")
    return "ASK_MB_NAME"


async def mb_save_business_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["business_name"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("Tech", callback_data="mbcat_Tech"),
         InlineKeyboardButton("Education", callback_data="mbcat_Education")],
        [InlineKeyboardButton("E-commerce", callback_data="mbcat_Ecommerce"),
         InlineKeyboardButton("Other", callback_data="mbcat_Other")],
    ]
    await update.message.reply_text(
        "📂 Choose your **Category**", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return "ASK_MB_CATEGORY"


async def mb_save_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("mbcat_", "")
    context.user_data["category"] = category

    await query.edit_message_text("✍ Add a short **Bio / Description**:")
    return "ASK_MB_BIO"


async def mb_save_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["bio"] = update.message.text
    await update.message.reply_text(
        "🤖 Send your **Bot Token** (From @BotFather)\n\n"
        "**Steps:**\n"
        "1️⃣ Open @BotFather\n"
        "2️⃣ Create New Bot\n"
        "3️⃣ Copy Bot Token\n"
        "4️⃣ Paste here 👇"
    )
    return "ASK_MB_TOKEN"


async def validate_bot_token(token: str):
    url = f"https://api.telegram.org/bot{token}/getMe"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response.status == 200


async def mb_save_bot_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_token = update.message.text.strip()

    valid = await validate_bot_token(bot_token)
    if not valid:
        await update.message.reply_text("❌ Invalid Bot Token. Please send again.")
        return "ASK_MB_TOKEN"

    # SAVE TO DB
    trial_end_date = datetime.now() + timedelta(days=settings.TRIAL_MONTHS * 30)

    async for db in get_db():
        owner = Owner(
            telegram_id=str(update.effective_user.id),
            business_name=context.user_data["business_name"],
            category=context.user_data["category"],
            bio=context.user_data["bio"],
            bot_token=bot_token,
            subscription_plan="trial",
            trial_ends=trial_end_date,
            subscribed=False
        )
        db.add(owner)
        await db.commit()

    await update.message.reply_text(
        "🎉 **Your Mini Bot Has Been Successfully Linked!**\n\n"
        f"🆓 You are now in **Free Trial ({settings.TRIAL_MONTHS} Months)**\n"
        f"Trial Ends: `{trial_end_date.strftime('%d-%m-%Y')}`\n\n"
        "This Bot was made using @Connectsprobot"
    )