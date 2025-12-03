"""
Admin-only commands (restricted by ADMIN_IDS).
"""
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()

# Parse admin IDs from environment variable
ADMIN_IDS = []
admin_ids_str = os.getenv('ADMIN_IDS', '')
if admin_ids_str:
    ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(',') if x.strip().isdigit()]


def admin_only(func):
    """Decorator to restrict command to admin users only."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text('⛔ Unauthorized: Admin access required.')
            return
        return await func(update, context)
    return wrapper


@admin_only
async def admin_panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display admin panel with available commands."""
    admin_text = (
        "🔐 *Admin Panel*\n\n"
        "Available commands:\n"
        "• `/list_owners` - List all registered owners\n"
        "• `/verify_owner <id>` - Verify an owner\n"
        "• `/broadcast <message>` - Send message to all users\n"
        "• `/stats` - View bot statistics\n"
        "• `/ban_user <id>` - Ban a user\n"
    )
    await update.message.reply_text(admin_text, parse_mode='Markdown')


@admin_only
async def list_owners_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all registered owners."""
    from database import AsyncSessionLocal, Owner
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Owner))
        owners = result.scalars().all()
        
        if not owners:
            await update.message.reply_text("No owners registered yet.")
            return
        
        text = "📋 *Registered Owners:*\n\n"
        for owner in owners:
            verified = "✅" if owner.verified else "❌"
            text += f"• {owner.name} (ID: {owner.telegram_id}) {verified}\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')


@admin_only
async def bot_stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display bot statistics."""
    from database import AsyncSessionLocal, Owner, User, Conversation
    from sqlalchemy import select, func
    
    async with AsyncSessionLocal() as session:
        owners_count = await session.execute(select(func.count(Owner.id)))
        users_count = await session.execute(select(func.count(User.id)))
        convos_count = await session.execute(select(func.count(Conversation.id)))
        
        stats_text = (
            "📊 *Bot Statistics*\n\n"
            f"👥 Total Owners: {owners_count.scalar()}\n"
            f"👤 Total Users: {users_count.scalar()}\n"
            f"💬 Total Conversations: {convos_count.scalar()}\n"
        )
        await update.message.reply_text(stats_text, parse_mode='Markdown')
