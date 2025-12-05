"""
messaging.py - Handle user messages and replies
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
from database import SessionLocal, MessageLog, Owner
from sqlalchemy.future import select

async def user_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    async with SessionLocal() as db:
        msg = MessageLog(
            user_id=str(user.id),
            message=update.message.text,
            timestamp=datetime.now(),
        )
        db.add(msg)
        await db.commit()

    async with SessionLocal() as db:
        result = await db.execute(select(Owner))
        owner = result.scalars().first()

    if not owner:
        return

    keyboard = [[InlineKeyboardButton("Reply", callback_data=f"reply_{user.id}")]]

    await context.bot.send_message(
        chat_id=int(owner.telegram_id),
        text=f"💬 Message from *{user.full_name}*\n\n📩 {update.message.text}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

    await update.message.reply_text("📨 *Your message has been sent.*\nThe admin will reply soon.", parse_mode="Markdown")

async def reply_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.data.replace("reply_", "")
    context.user_data["reply_to"] = user_id
    await query.edit_message_text("✍ *Send your reply:*", parse_mode="Markdown")

async def send_owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_msg = update.message.text
    user_id = context.user_data.get("reply_to")

    if user_id:
        await context.bot.send_message(
            chat_id=int(user_id),
            text=f"📨 *Reply from Admin:*\n\n{reply_msg}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ *Reply sent successfully.*", parse_mode="Markdown")
        context.user_data["reply_to"] = None
        