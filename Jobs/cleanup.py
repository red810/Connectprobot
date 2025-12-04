"""
cleanup.py
Delete chat messages older than 72 days automatically.
Triggered on message receive or manual call.
"""

from database import *
from datetime import datetime, timedelta

async def delete_old_messages():
    threshold_date = datetime.now() - timedelta(days=72)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM messages WHERE timestamp < ?",
        (threshold_date.strftime("%Y-%m-%d %H:%M:%S"),)
    )
    conn.commit()
    conn.close()

    print("🗑 Removed chat history older than 72 days")