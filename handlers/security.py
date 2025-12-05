"""
security.py
Anti-spam protection: Prevent users from sending many msgs quickly
"""

from datetime import datetime, timedelta

user_last_msg = {}

def anti_spam(user_id):
    global user_last_msg
    now = datetime.now()

    if user_id in user_last_msg:
        diff = now - user_last_msg[user_id]
        if diff < timedelta(seconds=4):  # Spam limit 1 msg every 4 sec
            return False
    user_last_msg[user_id] = now
    return True