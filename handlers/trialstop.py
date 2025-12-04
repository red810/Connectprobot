"""
trialstop.py
Stop access if trial expired
"""

from database import get_owner
from datetime import datetime, timedelta
from config import settings

def trial_active(owner_id):
    owner = get_owner(owner_id)
    if not owner: return False

    start_date = datetime.strptime(owner[3], "%Y-%m-%d")
    trial_days = settings.TRIAL_MONTHS * 30
    expiry_date = start_date + timedelta(days=trial_days)

    return datetime.now() < expiry_date