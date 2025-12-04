"""
messaging.py
Handles:
- Saving messages
- Forwarding to Owner
- Replying back
- Auto timestamp save
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from database import get_db, Message, Owner
from sqlalchemy.future import select


async def user_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Save message to DB
    async for db in get_db():
        msg = Message(
            user_id=str(user.id),
            message=update.message.text,
            timestamp=datetime.now(),
        )
        db.add(msg)
        await db.commit()

    # Fetch Owner data
    async for db in get_db():
        result = await db.execute(select(Owner))
        owner = result.scalars().first()

    if owner is None:
        return

    keyboard = [
        [InlineKeyboardButton("Reply", callback_data=f"reply_{user.id}")]
    ]

    await context.bot.send_message(
        chat_id=int(owner.telegram_id),
        text=f"💬 Message from **{user.full_name}**\n\n"
             f"📩 {update.message.text}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(
        "📨 **Your message has been sent.**\nThe admin will reply soon.\n\n"
        "This Bot was made using @Connectsprobot"
    )


async def reply_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.data.replace("reply_", "")
    context.user_data["reply_to"] = user_id

    await query.edit_message_text("✍ **Send your reply:**")
    return "WAITING_OWNER_REPLY"


async def send_owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_msg = update.message.text
    user_id = context.user_data.get("reply_to")

    if user_id:
        await context.bot.send_message(
            chat_id=int(user_id),
            text=f"📨 **Reply from Admin:**\n\n{reply_msg}\n\nThis Bot was made using @Connectsprobot"
        )

        await update.message.reply_text("✅ **Reply sent successfully.**")

        context.user_data["reply_to"] = None