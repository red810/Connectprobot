"""
Utility functions for message styling and watermarking.
"""


def append_footer(text: str, include_branding: bool = True) -> str:
    """Append 'Powered by' footer to messages."""
    if not include_branding:
        return text
    return f"{text}\n\n——\n🤖 Powered by ConnectProBot"


def make_intro_for_user(channel_name: str = None) -> str:
    """Create welcome intro message for users."""
    if channel_name:
        header = f"👋 *Welcome to {channel_name}!*\n\n"
    else:
        header = "👋 *Welcome to ConnectProBot!*\n\n"
    
    intro = (
        f"{header}"
        "Through this bot, you can safely connect and message "
        "Telegram channel or business owners.\n\n"
        "*💼 How it works:*\n"
        "1️⃣ If you came here via a channel link, your messages "
        "go directly to that owner.\n"
        "2️⃣ The owner can reply to you privately — without "
        "sharing any personal info.\n\n"
        "🔒 *Privacy Protected* | ⚡ *Fast Replies*\n\n"
        "🤖 _Powered by ConnectProBot — Connecting Creators with Their Audience!_"
    )
    return intro


def format_user_message(user_name: str, user_id: int, message: str) -> str:
    """Format a user message for forwarding to owner."""
    return (
        f"📨 *New Message*\n\n"
        f"👤 From: {user_name}\n"
        f"🆔 ID: `{user_id}`\n\n"
        f"💬 Message:\n{message}"
    )


def format_owner_reply(owner_name: str, message: str) -> str:
    """Format an owner reply for sending to user."""
    return (
        f"📩 *Reply from {owner_name}*\n\n"
        f"{message}\n\n"
        "——\n"
        "🤖 _Powered by ConnectProBot_"
    )
