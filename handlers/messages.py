"""
Handle user-to-owner messaging and owner replies (proxy).
"""
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from utils.branding import make_intro_for_user
from database import AsyncSessionLocal, Owner, User, Conversation


async def start_for_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When a user starts the bot normally, show intro."""
    text = make_intro_for_user()
    await update.message.reply_text(text)


async def direct_message_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Proxy a user's message to the correct owner.
    Deep link format: /start owner_<owner_telegram_id>
    """
    args = context.args or []
    
    # Check if user came via owner deep link
    if args and args[0].startswith('owner_'):
        try:
            owner_tid = int(args[0].split('_', 1)[1])
        except (ValueError, IndexError):
            await start_for_user(update, context)
            return
        
        tg_user = update.effective_user
        
        async with AsyncSessionLocal() as session:
            # Find the owner
            owner_result = await session.execute(
                select(Owner).where(Owner.telegram_id == owner_tid)
            )
            owner = owner_result.scalars().first()
            
            if not owner:
                await update.message.reply_text(
                    "❌ Owner not found. Please check the link and try again."
                )
                return
            
            if not owner.active:
                await update.message.reply_text(
                    "⚠️ This owner's bot is currently inactive."
                )
                return
            
            # Find or create user
            user_result = await session.execute(
                select(User).where(User.telegram_id == tg_user.id)
            )
            user = user_result.scalars().first()
            
            if not user:
                user = User(
                    telegram_id=tg_user.id,
                    first_name=tg_user.first_name or '',
                    last_name=tg_user.last_name or '',
                    username=tg_user.username or ''
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            
            # Store owner context for future messages
            context.user_data['connected_owner_id'] = owner.id
            context.user_data['connected_owner_tid'] = owner_tid
            
            # Send welcome message
            welcome_text = (
                f"👋 Welcome! You're now connected to *{owner.name}*.\n\n"
                f"📝 {owner.bio}\n\n"
                "Send your message and they will reply privately.\n\n"
                "🔒 Your identity is protected."
            )
            await update.message.reply_text(welcome_text, parse_mode='Markdown')
    else:
        # No deep link, show general intro
        await start_for_user(update, context)


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages from users to forward to owners."""
    owner_tid = context.user_data.get('connected_owner_tid')
    
    if not owner_tid:
        # User not connected to any owner
        await update.message.reply_text(
            "💡 To message a channel owner, use their specific bot link.\n\n"
            "Type /help for more information."
        )
        return
    
    # Forward the message to owner
    user = update.effective_user
    message_text = update.message.text or "[Media message]"
    
    forward_text = (
        f"📨 *New message from user*\n\n"
        f"👤 From: {user.first_name or 'Anonymous'}"
        f"{' (@' + user.username + ')' if user.username else ''}\n"
        f"🆔 User ID: `{user.id}`\n\n"
        f"💬 Message:\n{message_text}"
    )
    
    try:
        await context.bot.send_message(
            chat_id=owner_tid,
            text=forward_text,
            parse_mode='Markdown'
        )
        await update.message.reply_text("✅ Message sent to owner!")
    except Exception as e:
        await update.message.reply_text(
            "❌ Failed to deliver message. The owner may have blocked the bot."
        )


async def handle_owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle owner replies to users (via reply to forwarded message)."""
    # Check if this is a reply to a forwarded message
    if not update.message.reply_to_message:
        return
    
    reply_msg = update.message.reply_to_message
    
    # Extract user ID from the forwarded message
    # This requires parsing the message or storing metadata
    # For now, owners can use /reply <user_id> <message> command
    pass
