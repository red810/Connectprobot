# main.py
import logging, random, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_ADMIN = int(os.getenv("ADMIN_ID") or 0)

# --- Helper UI ---
def owner_main_keyboard():
    kb = [
        [InlineKeyboardButton("📊 My Stats", callback_data="stats") , InlineKeyboardButton("✏️ Edit Profile", callback_data="edit_profile")],
        [InlineKeyboardButton("➕ Add Channel", callback_data="add_channel"), InlineKeyboardButton("💎 Upgrade Plan", callback_data="premium")],
        [InlineKeyboardButton("📣 Broadcast", callback_data="broadcast"), InlineKeyboardButton("❓ Support", callback_data="support")]
    ]
    return InlineKeyboardMarkup(kb)

def user_start_keyboard():
    kb = [[InlineKeyboardButton("📢 Register your Channel", callback_data="register")]]
    return InlineKeyboardMarkup(kb)

# --- Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    # if started with owner link
    if args and args[0].startswith("owner_"):
        try:
            owner_id = int(args[0].split("_")[1])
            db.ensure_user(user_id)
            db.add_analytic(owner_id, "user_started_via_link", str(user_id))
            context.user_data["connected_owner"] = owner_id
            alias = db.get_user_alias(user_id) or f"User#{random.randint(1000,9999)}"
            await update.message.reply_text(
                f"You're now connected to the owner. Send your message below 👇"
            )
            return
        except Exception:
            await update.message.reply_text("Invalid or expired channel link.")
            return

    # if owner
    if db.is_owner_registered(user_id):
        await update.message.reply_text(
            "Welcome back, Channel Owner!\nUse the dashboard below to manage your profile.",
            reply_markup=owner_main_keyboard()
        )
    else:
        await update.message.reply_text(
            "👋 Welcome to ConnectProBot!\nYou can register your channel to receive messages from users safely.",
            reply_markup=user_start_keyboard()
        )

# Callback for inline buttons: registration, dashboard actions
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    # registration start
    if data == "register":
        await query.message.reply_text("Please enter your channel/business name:")
        context.user_data["awaiting_channel_name"] = True
        return

    if data == "add_channel":
        await query.message.reply_text("Send the new channel name you want to add:")
        context.user_data["awaiting_new_channel"] = True
        return

    if data == "edit_profile":
        kb = [
            [InlineKeyboardButton("Change Description", callback_data="edit_description")],
            [InlineKeyboardButton("Change Category", callback_data="edit_category")],
            [InlineKeyboardButton("Upload Logo", callback_data="upload_logo")]
        ]
        await query.message.reply_text("Choose field to edit:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "stats":
        stats = db.owner_stats(user_id)
        await query.message.reply_text(f"📊 Stats:\nMessages forwarded: {stats['messages_forwarded']}\nUnique users: {stats['unique_users']}")
        return

    if data == "premium":
        await query.message.reply_text("💎 Premium Plans:\nGold - priority routing, analytics\nPlatinum - everything + branding\n(Upgrade flow currently manual — contact admin)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Contact Admin", callback_data="contact_admin")]]))
        return

    if data == "contact_admin":
        await query.message.reply_text("Request sent to admin. They will contact you soon.")
        if BOT_ADMIN:
            await context.bot.send_message(BOT_ADMIN, f"Owner {user_id} requested premium info.")
        return

    if data == "support":
        await query.message.reply_text("Support: @YourSupportHandle or use /help")
        return

    if data == "broadcast":
        await query.message.reply_text("Broadcast feature is premium. Contact admin to unlock.")
        return

    # edit subfields
    if data == "edit_description":
        await query.message.reply_text("Send new short description (max 200 chars):")
        context.user_data["awaiting_description"] = True
        return
    if data == "edit_category":
        kb = [
            [InlineKeyboardButton("Tech", callback_data="cat:Tech"), InlineKeyboardButton("Education", callback_data="cat:Education")],
            [InlineKeyboardButton("Entertainment", callback_data="cat:Entertainment"), InlineKeyboardButton("E-commerce", callback_data="cat:E-commerce")]
        ]
        await query.message.reply_text("Choose category:", reply_markup=InlineKeyboardMarkup(kb))
        return
    if data and data.startswith("cat:"):
        cat = data.split("cat:")[1]
        db.set_owner_field(user_id, "category", cat)
        await query.message.reply_text(f"Category set to: {cat}")
        return

# Message handler (both users and owners)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    # If awaiting channel name (owner registration)
    if context.user_data.get("awaiting_channel_name"):
        channel_name = text[:100]
        db.register_owner(user_id, update.effective_user.username or str(user_id))
        start_link = f"https://t.me/{(os.getenv('BOT_USERNAME') or 'ConnectProBot')}?start=owner_{user_id}"
        db.add_channel(user_id, channel_name, start_link=start_link)
        context.user_data["awaiting_channel_name"] = False
        await update.message.reply_text(f"✅ Channel '{channel_name}' registered!\nYour link:\n{start_link}", reply_markup=owner_main_keyboard())
        return

    # Add channel flow
    if context.user_data.get("awaiting_new_channel"):
        channel_name = text[:100]
        start_link = f"https://t.me/{(os.getenv('BOT_USERNAME') or 'ConnectProBot')}?start=owner_{user_id}"
        db.add_channel(user_id, channel_name, start_link=start_link)
        context.user_data["awaiting_new_channel"] = False
        await update.message.reply_text(f"✅ Channel '{channel_name}' added.\nLink: {start_link}")
        return

    # edit description
    if context.user_data.get("awaiting_description"):
        desc = text[:200]
        db.set_owner_field(user_id, "description", desc)
        context.user_data["awaiting_description"] = False
        await update.message.reply_text("✅ Description updated.")
        return

    # If user is connected to an owner (via link)
    connected_owner = context.user_data.get("connected_owner")
    if connected_owner:
        db.ensure_user(user_id)
        alias = db.get_user_alias(user_id) or f"User#{random.randint(1000,9999)}"
        # forward message to owner (send text)
        msg_text = f"💬 Message from {alias} (via your ConnectPro link):\n\n{text}\n\nReply to this message to respond to the user."
        sent = await context.bot.send_message(connected_owner, msg_text)
        db.save_forwarded_map(sent.message_id, user_id, connected_owner)
        db.add_analytic(connected_owner, "message_forwarded", str(user_id))
        await update.message.reply_text("✅ Your message has been sent to the owner. They will reply here.")
        return

    # If owner replies to a forwarded message (owner must reply to bot's forwarded message)
    if db.is_owner_registered(user_id):
        if update.message.reply_to_message:
            replied_msg_id = update.message.reply_to_message.message_id
            target_user_id, owner_in_map = db.get_user_by_forwarded_msg(replied_msg_id)
            if target_user_id:
                owner_info = db.get_owner(user_id)
                owner_name = owner_info[1] if owner_info else "Owner"
                await context.bot.send_message(target_user_id, f"📩 Reply from {owner_name}:\n\n{text}")
                await update.message.reply_text("✅ Your reply has been sent to the user.")
                db.add_analytic(user_id, "owner_replied", str(target_user_id))
            else:
                await update.message.reply_text("⚠️ Please reply to a user's forwarded message to respond.")
        else:
            await update.message.reply_text("Tap reply on the forwarded user message then type your reply. Use /menu to open dashboard.", reply_markup=owner_main_keyboard())
        return

    # default fallback
    await update.message.reply_text("Hi! To connect to a channel owner, open the owner's link or use /start. If you're owner, use /start then Register.")

# Admin command: view owners list (admin only)
async def admin_owners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != BOT_ADMIN:
        await update.message.reply_text("Unauthorized.")
        return
    conn = db.get_conn()
    c = conn.cursor()
    c.execute("SELECT owner_id, username, premium_status FROM owners ORDER BY registered_at DESC LIMIT 100")
    rows = c.fetchall()
    conn.close()
    if not rows:
        await update.message.reply_text("No owners registered yet.")
        return
    lines = [f"{r[0]} — @{r[1]} — {r[2]}" for r in rows]
    await update.message.reply_text("Owners:\n" + "\n".join(lines))

# post init to print bot username
async def post_init(app):
    bot_info = await app.bot.get_me()
    print("Bot ready:", bot_info.username)
    if not os.getenv("BOT_USERNAME"):
        os.environ["BOT_USERNAME"] = bot_info.username

def build_app():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is required")
    app = ApplicationBuilder().token(token).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("admin_owners", admin_owners))
    return app

if __name__ == "__main__":
    import asyncio
    db.init_db()
    async def main():
        application = build_app()
        print("Bot running...")
        await application.run_polling()
    asyncio.run(main())
