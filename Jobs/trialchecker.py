"""
trialchecker.py
Checks if owner's free trial expired.
If expired — bot functions stop except renewal message.
"""

from database import *
from datetime import datetime, timedelta
from config import settings
from telegram import Bot

async def check_trial(bot_token):
    bot = Bot(token=bot_token)
    owners = get_all_owners()

    for owner in owners:
        start_date = datetime.strptime(owner[3], "%Y-%m-%d")
        trial_days = settings.TRIAL_MONTHS * 30
        expiry_date = start_date + timedelta(days=trial_days)
        now = datetime.now()

        if now > expiry_date:
            try:
                await bot.send_message(
                    chat_id=owner[0],
                    text=(
                        f"⚠ **Your Free Trial Has Ended**\n\n"
                        "Your bot is currently paused.\n"
                        "Upgrade to activate again.\n\n"
                        "This Bot was made using @Connectsprobot"
                    ),
                )
            except:
                pass
            
        elif (expiry_date - now).days == 1:
            try:
                await bot.send_message(
                    chat_id=owner[0],
                    text=(
                        "⏳ **Reminder**\n"
                        "Your free trial ends in **24 hours**.\n"
                        "Upgrade to keep your bot online.\n"
                    ),
                )
            except:
                pass