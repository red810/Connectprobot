"""
trialstop.py - Check if trial is active
"""
from database import get_owner_by_telegram_id
from datetime import datetime

async def trial_active(owner_id):
    owner = await get_owner_by_telegram_id(str(owner_id))
    if not owner or not owner.trial_ends:
        return False
    return datetime.now() < owner.trial_ends
    