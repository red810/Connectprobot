"""
Owner dashboard commands and menu.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select
from utils.branding import append_footer
from database import AsyncSessionLocal, Owner, Conversation


async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display dashboard menu for owner."""
    user_id = update.effective_user.id
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Owner).where(Owner.telegram_id == user_id)
        )
        owner = result.scalars().first()
        
        if not owner:
            await update.message.reply_text(
                '❌ You don\'t have an account yet.\n'
                'Use /owner to create your bot.'
            )
            return
        
        verified_badge = ' ✅' if owner.verified else ''
        plan_badge = '⭐ Premium' if owner.plan == 'premium' else '🆓 Basic'
        
        header = (
            f'📊 *Dashboard - {owner.name}*{verified_badge}\n'
            f'Plan: {plan_badge}\n'
            '─────────────────\n'
        )
    
    kb = [
        [InlineKeyboardButton('📈 My Stats', callback_data='dash_stats'),
         InlineKeyboardButton('💬 Messages', callback_data='dash_messages')],
        [InlineKeyboardButton('🔍 Filter Messages', callback_data='dash_filter'),
         InlineKeyboardButton('🧾 Logs', callback_data='dash_logs')],
        [InlineKeyboardButton('💰 Subscription', callback_data='dash_sub'),
         InlineKeyboardButton('🧠 Auto-Reply', callback_data='dash_autoreply')],
        [InlineKeyboardButton('⚙️ Settings', callback_data='dash_settings'),
         InlineKeyboardButton('👥 User List', callback_data='dash_users')],
        [InlineKeyboardButton('🔗 Get Bot Link', callback_data='dash_link')],
        [InlineKeyboardButton('❓ Help / Support', callback_data='dash_help')]
    ]
    
    await update.message.reply_text(
        append_footer(header + 'Choose an action:'),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode='Markdown'
    )


async def dashboard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle dashboard button callbacks."""
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Owner).where(Owner.telegram_id == user_id)
        )
        owner = result.scalars().first()
        
        if not owner:
            await query.message.reply_text('❌ Account not found.')
            return
    
    if data == 'dash_stats':
        # Show statistics
        stats_text = (
            '📊 *Your Statistics*\n\n'
            '📨 Total Messages: 0\n'
            '👥 Unique Users: 0\n'
            '📈 This Week: 0\n'
            '⏱️ Avg Response Time: N/A\n\n'
            '_Statistics update in real-time_'
        )
        await query.message.reply_text(stats_text, parse_mode='Markdown')
        
    elif data == 'dash_messages':
        await query.message.reply_text(
            '💬 *Recent Messages*\n\n'
            'No messages yet.\n'
            'Share your bot link to start receiving messages!',
            parse_mode='Markdown'
        )
        
    elif data == 'dash_filter':
        kb = [
            [InlineKeyboardButton('🛒 Orders', callback_data='filter_order'),
             InlineKeyboardButton('❓ Queries', callback_data='filter_query')],
            [InlineKeyboardButton('🛠️ Support', callback_data='filter_support'),
             InlineKeyboardButton('📋 All', callback_data='filter_all')]
        ]
        await query.message.reply_text(
            '🔍 *Filter Messages By:*',
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )
        
    elif data == 'dash_logs':
        await query.message.reply_text(
            '🧾 *Message Logs*\n\n'
            'Last 10 conversations will appear here.\n'
            '_No conversations yet._',
            parse_mode='Markdown'
        )
        
    elif data == 'dash_sub':
        plan = '⭐ Premium' if owner.plan == 'premium' else '🆓 Basic'
        expires = owner.subscription_expires.strftime('%Y-%m-%d') if owner.subscription_expires else 'N/A'
        
        sub_text = (
            f'💰 *Subscription Details*\n\n'
            f'Current Plan: {plan}\n'
            f'Expires: {expires}\n\n'
        )
        
        kb = []
        if owner.plan == 'basic':
            kb.append([InlineKeyboardButton('⬆️ Upgrade to Premium', callback_data='upgrade_premium')])
        else:
            kb.append([InlineKeyboardButton('🔄 Renew Subscription', callback_data='renew_sub')])
        
        await query.message.reply_text(
            sub_text,
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )
        
    elif data == 'dash_autoreply':
        kb = [
            [InlineKeyboardButton('➕ Add Auto-Reply', callback_data='ar_add')],
            [InlineKeyboardButton('📋 View Auto-Replies', callback_data='ar_list')],
            [InlineKeyboardButton('🔄 Toggle On/Off', callback_data='ar_toggle')]
        ]
        await query.message.reply_text(
            '🧠 *Auto-Reply Settings*\n\n'
            'Set up automatic responses for common questions.',
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )
        
    elif data == 'dash_settings':
        kb = [
            [InlineKeyboardButton('✏️ Edit Name', callback_data='set_name'),
             InlineKeyboardButton('📝 Edit Bio', callback_data='set_bio')],
            [InlineKeyboardButton('🖼️ Change Logo', callback_data='set_logo'),
             InlineKeyboardButton('📂 Category', callback_data='set_category')],
            [InlineKeyboardButton('🔔 Notifications', callback_data='set_notif'),
             InlineKeyboardButton('🚫 Block List', callback_data='set_block')]
        ]
        await query.message.reply_text(
            '⚙️ *Settings*\n\n'
            f'Name: {owner.name}\n'
            f'Category: {owner.category}\n'
            f'Bio: {owner.bio[:50]}...' if owner.bio else 'Bio: Not set',
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )
        
    elif data == 'dash_users':
        await query.message.reply_text(
            '👥 *User List*\n\n'
            'Users who have messaged you:\n\n'
            '_No users yet._',
            parse_mode='Markdown'
        )
        
    elif data == 'dash_link':
        bot_link = f't.me/{context.bot.username}?start=owner_{user_id}'
        await query.message.reply_text(
            '🔗 *Your Bot Link*\n\n'
            f'`{bot_link}`\n\n'
            'Share this link in your:\n'
            '• Channel bio\n'
            '• Post descriptions\n'
            '• Social media\n\n'
            'Anyone who clicks can message you anonymously!',
            parse_mode='Markdown'
        )
        
    elif data == 'dash_help':
        help_text = (
            '❓ *Help & Support*\n\n'
            '*Commands:*\n'
            '/start - Start the bot\n'
            '/owner - Create new bot\n'
            '/dashboard - Open dashboard\n'
            '/help - Show this help\n\n'
            '*Support:*\n'
            '📧 Email: support@connectprobot.com\n'
            '💬 Telegram: @ConnectProSupport\n\n'
            '📚 Documentation: docs.connectprobot.com'
        )
        await query.message.reply_text(help_text, parse_mode='Markdown')
        
    else:
        await query.message.reply_text('🚧 Feature coming soon!')
