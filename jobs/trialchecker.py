"""
trialchecker.py - Check owner trial expiry
"""
from database import SessionLocal, Owner
from datetime import datetime, timedelta
from sqlalchemy.future import select
from telegram import Bot

async def check_trial(bot_token):
    bot = Bot(token=bot_token)
    
    async with SessionLocal() as session:
        result = await session.execute(select(Owner))
        owners = result.scalars().all()

    now = datetime.now()

    for owner in owners:
        if not owner.trial_ends:
            continue
            
        expiry_date = owner.trial_ends

        if now > expiry_date:
            try:
                await bot.send_message(
                    chat_id=int(owner.telegram_id),
                    text="⚠ *Your Free Trial Has Ended*\n\nYour bot is paused.\nUpgrade to activate again.",
                    parse_mode="Markdown"
                )
            except:
                pass
                
        elif (expiry_date - now).days == 1:
            try:
                await bot.send_message(
                    chat_id=int(owner.telegram_id),
                    text="⏳ *Reminder*\nYour trial ends in *24 hours*.",
                    parse_mode="Markdown"
                )
            except:
                pass
                