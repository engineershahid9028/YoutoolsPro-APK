from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from binance_verify import verify_usdt_payment
from db_service import (
    get_or_create_user, is_premium, set_premium, revoke_premium,
    ban_user, unban_user, is_banned, get_stats, get_all_users,
    get_all_payments, log_payment, log_tool_usage,
    create_ticket, get_ticket, reply_ticket, close_ticket,
    get_open_tickets, get_promo
)

from tools_engine import (
    keyword_generator, title_generator, seo_analyzer, rank_tracker,
    competitor_spy, viral_ideas, content_generator,
    trending_videos, thumbnail_ai, growth_mentor
)

from pdf_engine import generate_pdf

ADMIN_ID = 7575476523
FREE_TOOLS = ["keyword", "title", "rank"]

BINANCE_PAY_ID = "339696746"
USDT_WALLET = "TCmgNUz3nrMSQ1xjCALwcXQs8EJLwh4c5i"
CHANNEL_URL = "https://t.me/YouToolsPro"


# =========================
# MENUS
# =========================

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Keyword", callback_data="keyword"),
         InlineKeyboardButton("🏷 Title", callback_data="title")],

        [InlineKeyboardButton("🔍 SEO", callback_data="seo"),
         InlineKeyboardButton("📊 Rank", callback_data="rank")],

        [InlineKeyboardButton("🕵️ Competitor", callback_data="spy"),
         InlineKeyboardButton("🖼 Thumbnail", callback_data="thumbnail")],

        [InlineKeyboardButton("🔥 Viral", callback_data="viral"),
         InlineKeyboardButton("📝 Content", callback_data="content")],

        [InlineKeyboardButton("📈 Trending", callback_data="trending"),
         InlineKeyboardButton("💡 Growth", callback_data="growth")],

        [InlineKeyboardButton("💎 Premium", callback_data="premium")],
        [InlineKeyboardButton("🏷 Promo", callback_data="promo")],
        [InlineKeyboardButton("🎟 Support", callback_data="support")],
        [InlineKeyboardButton("📢 Channel", url=CHANNEL_URL)]
    ])


def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
         InlineKeyboardButton("👥 Users", callback_data="admin_users")],

        [InlineKeyboardButton("💳 Payments", callback_data="admin_payments")],
        [InlineKeyboardButton("✅ Grant", callback_data="admin_grant"),
         InlineKeyboardButton("❌ Revoke", callback_data="admin_revoke")],

        [InlineKeyboardButton("🚫 Ban", callback_data="admin_ban"),
         InlineKeyboardButton("♻ Unban", callback_data="admin_unban")],

        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")]
    ])


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if is_banned(user_id):
        await update.message.reply_text("🚫 You are banned.")
        return

    get_or_create_user(user_id)

    status = "👑 Admin" if user_id == ADMIN_ID else "💎 Premium" if is_premium(user_id) else "🆓 Free"

    await update.message.reply_text(
        f"🚀 YouToolsPro AI Dashboard\n\nAccount Status: {status}",
        reply_markup=main_menu()
    )


# =========================
# ADMIN
# =========================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("👑 Admin Panel", reply_markup=admin_menu())


# =========================
# BUTTONS
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    action = query.data

    if action.startswith("admin_"):
        if user_id != ADMIN_ID:
            return

        if action == "admin_stats":
            users, premium, wallets, total = get_stats()
            await query.message.reply_text(
                f"Users: {users}\nPremium: {premium}\nWallets: {wallets}\nRequests: {total}"
            )
            return

        if action == "admin_users":
            users = get_all_users()
            msg = "\n".join(f"{u.telegram_id} | {u.is_premium}" for u in users)
            await query.message.reply_text(msg[:4000])
            return

        if action == "admin_payments":
            payments = get_all_payments()
            msg = "\n".join(f"{p.user_id} | {p.amount} | {p.status}" for p in payments)
            await query.message.reply_text(msg[:4000])
            return

        context.user_data["admin_action"] = action
        await query.message.reply_text("Send USER ID")
        return

    if user_id != ADMIN_ID and action not in FREE_TOOLS and not is_premium(user_id) and action not in ["premium", "promo", "support"]:
        await query.message.reply_text("🔒 Premium required")
        return

    context.user_data["tool"] = action
    await query.message.reply_text("Send input")


# =========================
# TEXT
# =========================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    admin_action = context.user_data.get("admin_action")
    if admin_action and user_id == ADMIN_ID:
        uid = int(text)

        if admin_action == "admin_grant":
            set_premium(uid)
            await update.message.reply_text("✅ Granted")

        elif admin_action == "admin_revoke":
            revoke_premium(uid)
            await update.message.reply_text("❌ Revoked")

        elif admin_action == "admin_ban":
            ban_user(uid)
            await update.message.reply_text("🚫 Banned")

        elif admin_action == "admin_unban":
            unban_user(uid)
            await update.message.reply_text("♻ Unbanned")

        context.user_data["admin_action"] = None
        return

    tool = context.user_data.get("tool")
    if not tool:
        return

    await update.message.reply_text("⏳ Processing...")

    engines = {
        "keyword": keyword_generator,
        "title": title_generator,
        "seo": seo_analyzer,
        "rank": rank_tracker,
        "spy": competitor_spy,
        "viral": viral_ideas,
        "content": content_generator,
        "trending": trending_videos,
        "thumbnail": thumbnail_ai,
        "growth": growth_mentor
    }

    result = engines[tool](text)

    # 🔒 PROTECT AGAINST EMPTY RESULT
    if not result or not result.strip():
        result = "⚠️ Tool failed to generate a result. Please try again."

    log_tool_usage(user_id, tool, text)

    pdf = generate_pdf(user_id, tool, result)

    await update.message.reply_text(result)
    await context.bot.send_document(user_id, open(pdf, "rb"))

    context.user_data["tool"] = None


# =========================
# PAYMENT
# =========================

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("Usage: /paid TXID")
        return

    txid = context.args[0]

    if not verify_usdt_payment(txid):
        log_payment(user_id, txid, 5, "failed")
        await update.message.reply_text("❌ Invalid TXID")
        return

    set_premium(user_id)
    log_payment(user_id, txid, 5, "success")

    await update.message.reply_text("✅ Premium activated")


# =========================
# BALANCE
# =========================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(update.effective_user.id)
    await update.message.reply_text(f"Wallet: {user.wallet} USDT")


# =========================
# PROMO
# =========================

async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏷 Use promo in dashboard")
