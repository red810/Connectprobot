"""
Handles owner onboarding and subscription selections.
"""
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select
from utils.branding import append_footer
from utils.payments import generate_payment_link
from database import AsyncSessionLocal, Owner


async def start_owner_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show initial options for owner onboarding."""
    kb = [
        [InlineKeyboardButton('🚀 Start My Own Bot', callback_data='start_own')],
        [InlineKeyboardButton('⚙️ Manage Existing Account', callback_data='manage_existing')]
    ]
    text = (
        "👋 *Welcome to ConnectProBot!*\n\n"
        "Create your own connect bot for your Telegram channel or business.\n\n"
        "Choose an option below:"
    )
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode='Markdown'
    )


async def owner_callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle owner's inline button clicks for onboarding."""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == 'start_own':
        await query.message.reply_text(
            '1️⃣ *Step 1/5*\n\nEnter your business or channel name:',
            parse_mode='Markdown'
        )
        context.user_data['onboarding_step'] = 'name'
    elif data == 'manage_existing':
        # Check if user has existing account
        user_id = update.effective_user.id
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Owner).where(Owner.telegram_id == user_id)
            )
            owner = result.scalars().first()
            
            if owner:
                await query.message.reply_text(
                    f'✅ Found your account: *{owner.name}*\n\n'
                    'Use /dashboard to manage your settings.',
                    parse_mode='Markdown'
                )
            else:
                await query.message.reply_text(
                    '❌ No existing account found.\n'
                    'Use /owner to create a new bot.'
                )


async def owner_message_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle step-by-step onboarding questions."""
    step = context.user_data.get('onboarding_step')
    text = update.message.text if update.message else ''
    
    if not step:
        return  # Not in onboarding flow
    
    if step == 'name':
        if len(text) < 2:
            await update.message.reply_text('❌ Name too short. Please enter a valid name.')
            return
        context.user_data['name'] = text
        context.user_data['onboarding_step'] = 'category'
        
        kb = [
            [InlineKeyboardButton('💻 Tech', callback_data='cat_tech'),
             InlineKeyboardButton('📚 Education', callback_data='cat_education')],
            [InlineKeyboardButton('🛒 E-commerce', callback_data='cat_ecommerce'),
             InlineKeyboardButton('🎨 Creative', callback_data='cat_creative')],
            [InlineKeyboardButton('📰 News/Media', callback_data='cat_news'),
             InlineKeyboardButton('🔧 Other', callback_data='cat_other')]
        ]
        await update.message.reply_text(
            '2️⃣ *Step 2/5*\n\nChoose your category:',
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )
        return
    
    if step == 'bio':
        context.user_data['bio'] = text[:500]  # Limit bio length
        context.user_data['onboarding_step'] = 'logo'
        await update.message.reply_text(
            '4️⃣ *Step 4/5*\n\n'
            'Upload a logo (send as image)\n'
            'Or type /skip to continue without a logo.',
            parse_mode='Markdown'
        )
        return


async def category_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection."""
    query = update.callback_query
    await query.answer()
    
    category_map = {
        'cat_tech': 'Tech',
        'cat_education': 'Education',
        'cat_ecommerce': 'E-commerce',
        'cat_creative': 'Creative',
        'cat_news': 'News/Media',
        'cat_other': 'Other'
    }
    
    context.user_data['category'] = category_map.get(query.data, 'Other')
    context.user_data['onboarding_step'] = 'bio'
    
    await query.message.reply_text(
        '3️⃣ *Step 3/5*\n\nAdd a short bio/description (max 500 characters):',
        parse_mode='Markdown'
    )


async def owner_logo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Accept photo upload as logo and proceed to subscription options."""
    step = context.user_data.get('onboarding_step')
    
    if step != 'logo':
        return
    
    photos = update.message.photo
    if not photos:
        await update.message.reply_text('❌ No photo detected. Send an image or /skip')
        return
    
    file_id = photos[-1].file_id
    context.user_data['logo_file_id'] = file_id
    
    await show_subscription_options(update, context)


async def skip_logo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /skip command to skip logo upload."""
    step = context.user_data.get('onboarding_step')
    
    if step == 'logo':
        context.user_data['logo_file_id'] = None
        await show_subscription_options(update, context)


async def show_subscription_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display subscription plan options."""
    context.user_data['onboarding_step'] = 'plan'
    
    kb = [
        [InlineKeyboardButton('🆓 Basic (Free)', callback_data='plan_basic')],
        [InlineKeyboardButton('⭐ Premium ($9.99/mo)', callback_data='plan_premium')]
    ]
    
    text = (
        '5️⃣ *Step 5/5*\n\n'
        '*Choose a subscription plan:*\n\n'
        '🆓 *Basic (Free)*\n'
        '• Up to 100 messages/month\n'
        '• Basic analytics\n'
        '• ConnectProBot branding\n\n'
        '⭐ *Premium ($9.99/month)*\n'
        '• Unlimited messages\n'
        '• Advanced analytics\n'
        '• Custom branding\n'
        '• Priority support\n'
        '• Auto-reply features'
    )
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode='Markdown'
    )


async def plan_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plan selection and create owner account."""
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id
    
    async with AsyncSessionLocal() as session:
        # Check if owner already exists
        result = await session.execute(
            select(Owner).where(Owner.telegram_id == user_id)
        )
        existing = result.scalars().first()
        
        if existing:
            await query.message.reply_text(
                '⚠️ You already have an account. Use /dashboard to manage it.'
            )
            return
        
        # Create new owner
        owner = Owner(
            telegram_id=user_id,
            name=context.user_data.get('name', 'Unnamed'),
            category=context.user_data.get('category', 'Other'),
            bio=context.user_data.get('bio', ''),
            logo_file_id=context.user_data.get('logo_file_id')
        )
        
        if data == 'plan_basic':
            owner.plan = 'basic'
            owner.subscription_expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)
            session.add(owner)
            await session.commit()
            
            await query.message.reply_text(
                '✅ *Basic plan activated!*\n\n'
                f'Your bot link: `t.me/YourBotName?start=owner_{user_id}`\n\n'
                'Share this link in your channel bio or posts.\n'
                'Users who click it can message you anonymously!\n\n'
                'Use /dashboard to manage your bot.\n\n'
                '🤖 Powered by ConnectProBot',
                parse_mode='Markdown'
            )
            # Clear onboarding data
            context.user_data.clear()
            
        elif data == 'plan_premium':
            # Store pending owner for payment flow
            context.user_data['pending_owner'] = {
                'name': owner.name,
                'category': owner.category,
                'bio': owner.bio,
                'logo_file_id': owner.logo_file_id
            }
            
            kb = [
                [InlineKeyboardButton('💳 Pay via ConnectProBot', callback_data='pay_system')],
                [InlineKeyboardButton('🔗 Use Own Payment Link', callback_data='pay_own')]
            ]
            await query.message.reply_text(
                '💰 *Choose payment method:*',
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode='Markdown'
            )


async def payment_method_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment method selection."""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    pending = context.user_data.get('pending_owner')
    if not pending:
        await query.message.reply_text('❌ Session expired. Please start again with /owner')
        return
    
    if data == 'pay_own':
        await query.message.reply_text(
            '🔗 *Custom Payment Setup*\n\n'
            'Send me your payment gateway link.\n'
            'After payment is confirmed, your premium features will be activated.',
            parse_mode='Markdown'
        )
        context.user_data['onboarding_step'] = 'await_own_link'
        
    elif data == 'pay_system':
        user_id = update.effective_user.id
        link = await generate_payment_link(user_id, 'premium')
        
        kb = [[InlineKeyboardButton('💳 Pay Now', url=link)]]
        await query.message.reply_text(
            '💳 *Complete Payment*\n\n'
            'Click the button below to pay securely.\n'
            'Your premium features will activate automatically after payment.',
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )
