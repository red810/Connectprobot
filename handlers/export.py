"""
export.py
Exports conversation in JSON string format (owner download)
"""

import json
from database import get_messages_for_owner
from telegram import Update
from telegram.ext import ContextTypes

async def export_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id

    messages = get_messages_for_owner(user_id)

    export_data = []
    for msg in messages:
        export_data.append({
            "user_id": msg[1],
            "message": msg[2],
            "timestamp": msg[3]
        })

    json_data = json.dumps(export_data, indent=4)

    await update.message.reply_document(
        filename="ChatExport_ConnectsProBot.json",
        document=json_data.encode("utf-8"),
        caption="📁 Here is your chat export."
    )