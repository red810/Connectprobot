"""
cleanup.py - Delete messages older than 72 days
"""
from database import SessionLocal, MessageLog
from datetime import datetime, timedelta
from sqlalchemy import delete

async def delete_old_messages():
    threshold_date = datetime.now() - timedelta(days=72)
    
    async with SessionLocal() as session:
        await session.execute(
            delete(MessageLog).where(MessageLog.timestamp < threshold_date)
        )
        await session.commit()
    
    print("🗑 Removed chat history older than 72 days")
    