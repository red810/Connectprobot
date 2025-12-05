"""
export.py - Export messages as JSON
"""
import json
from database import get_owner_by_telegram_id, get_messages_for_owner
from telegram import Update
from telegram.ext import ContextTypes

async def export_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    
    owner = await get_owner_by_telegram_id(user_id)
    if not owner:
        await update.message.reply_text("❌ Owner not found.")
        return
    
    messages = await get_messages_for_owner(owner.id)
    
    export_data = [
        {
            "user_id": msg.user_id,
            "message": msg.message,
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]

    json_data = json.dumps(export_data, indent=4)

    await update.message.reply_document(
        document=json_data.encode("utf-8"),
        filename="ChatExport_ConnectsProBot.json",
        caption="📁 Here is your chat export."
    )
    