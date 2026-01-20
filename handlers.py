from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

from tools_engine import *
from binance_verify import verify_usdt_payment
from db_service import *
from pdf_engine import generate_pdf
from analytics import get_platform_stats


# =========================
# CONFIG
# =========================

ADMIN_ID = 7575476523
FREE_TOOLS = ["keyword", "title", "rank"]

BINANCE_PAY_ID = "339696746"
USDT_WALLET = "TCmgNUz3nrMSQ1xjCALwcXQs8EJLwh4c5i"
CHANNEL_URL = "https://t.me/YouToolsPro"


# =========================
# USER MENU
# =========================

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Keyword Generator", callback_data="keyword"),
         InlineKeyboardButton("🏷 Title Generator", callback_data="title")],

        [InlineKeyboardButton("🔍 SEO Analyzer", callback_data="seo"),
         InlineKeyboardButton("📊 Rank Tracker", callback_data="rank")],

        [InlineKeyboardButton("🕵️ Competitor Spy", callback_data="spy"),
         InlineKeyboardButton("🖼 Thumbnail AI", callback_data="thumbnail")],

        [InlineKeyboardButton("🔥 Viral Ideas", callback_data="viral"),
         InlineKeyboardButton("📝 Content Generator", callback_data="content")],

        [InlineKeyboardButton("📈 Trending Videos", callback_data="trending"),
         InlineKeyboardButton("💡 Growth Mentor", callback_data="growth")],

        [InlineKeyboardButton("💎 Premium (5 USDT)", callback_data="premium")],

        [InlineKeyboardButton("🎁 Referral Program", callback_data="referral"),
         InlineKeyboardButton("🏷 Promo Code", callback_data="promo")],

        [InlineKeyboardButton("🎟 Support", callback_data="support")],
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)]
    ])


# =========================
# ADMIN MENU
# =========================

def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
         InlineKeyboardButton("👥 Users", callback_data="admin_users")],

        [InlineKeyboardButton("💳 Payments", callback_data="admin_payments"),
         InlineKeyboardButton("🎟 Tickets", callback_data="admin_tickets")],

        [InlineKeyboardButton("✅ Grant Premium", callback_data="admin_grant"),
         InlineKeyboardButton("❌ Revoke Premium", callback_data="admin_revoke")],

        [InlineKeyboardButton("🚫 Ban User", callback_data="admin_ban"),
         InlineKeyboardButton("♻️ Unban User", callback_data="admin_unban")],

        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("💰 Wallets", callback_data="admin_wallets")]
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
        f"🚀 YouToolsPro AI Dashboard\n\n"
        f"All Tools to Rank, Trend & Monetize\n\n"
        f"Account Status: {status}",
        reply_markup=main_menu()
    )


# =========================
# ADMIN PANEL
# =========================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_menu())


# =========================
# BUTTON HANDLER
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    action = query.data


    # ================= ADMIN =================
    if action.startswith("admin_"):

        if user_id != ADMIN_ID:
            return

        if action == "admin_stats":
            users, premium, wallets, total_requests = get_stats()

            await query.message.reply_text(
                f"📊 Platform Stats\n\n"
                f"Users: {users}\n"
                f"Premium: {premium}\n"
                f"Wallets: {wallets} USDT\n"
                f"Tool Requests: {total_requests}"
            )
            return

        if action == "admin_users":
            users = get_all_users()
            msg = "👥 Users:\n\n"
            for u in users:
                msg += f"{u.telegram_id} | Premium: {u.is_premium} | Wallet: {u.wallet}\n"
            await query.message.reply_text(msg[:4000])
            return

        if action == "admin_wallets":
            users = get_all_users()
            msg = "💰 Wallets:\n\n"
            for u in users:
                msg += f"{u.telegram_id} → {u.wallet} USDT\n"
            await query.message.reply_text(msg[:4000])
            return

        if action == "admin_payments":
            payments = get_all_payments()
            msg = "💳 Payments:\n\n"
            for p in payments[:20]:
                msg += f"{p.user_id} | {p.amount} USDT | {p.status}\n"
            await query.message.reply_text(msg[:4000])
            return


        # ================= TICKETS WITH BUTTONS =================
        if action == "admin_tickets":
            tickets = get_open_tickets()

            if not tickets:
                await query.message.reply_text("✅ No open support tickets.")
                return

            for t in tickets:
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✏ Reply", callback_data=f"ticket_reply_{t.id}"),
                        InlineKeyboardButton("❌ Close", callback_data=f"ticket_close_{t.id}")
                    ]
                ])

                msg = (
                    f"🎟 Support Ticket\n\n"
                    f"🆔 Ticket ID: {t.id}\n"
                    f"👤 User: {t.user_id}\n\n"
                    f"📩 Message:\n{t.message}"
                )

                await query.message.reply_text(msg, reply_markup=keyboard)

            return

        context.user_data["admin_action"] = action
        await query.message.reply_text("Send USER_ID (or message for broadcast)")
        return


    # ================= TICKET BUTTONS =================
    if action.startswith("ticket_reply_"):

        if user_id != ADMIN_ID:
            return

        ticket_id = int(action.split("_")[-1])
        context.user_data["reply_ticket_id"] = ticket_id

        await query.message.reply_text(f"✏ Send reply message for Ticket #{ticket_id}")
        return


    if action.startswith("ticket_close_"):

        if user_id != ADMIN_ID:
            return

        ticket_id = int(action.split("_")[-1])
        close_ticket(ticket_id)

        await query.message.reply_text(f"✅ Ticket #{ticket_id} closed successfully")
        return


    # ================= USER =================
    if user_id != ADMIN_ID and action not in FREE_TOOLS and not is_premium(user_id) and action not in ["premium", "referral", "promo", "support"]:
        await query.message.reply_text("🔒 Premium users only.")
        return

    context.user_data["tool"] = action

    prompts = {
        "keyword": "🔑 Send topic",
        "title": "🏷 Send topic",
        "seo": "🔍 Send YouTube link",
        "rank": "📊 Send keyword",
        "spy": "🕵️ Send competitor channel",
        "thumbnail": "🖼 Send video topic",
        "viral": "🔥 Send niche",
        "content": "📝 Send topic",
        "trending": "📈 Send niche",
        "growth": "💡 Send channel niche"
    }

    if action in prompts:
        await query.message.reply_text(prompts[action])

    elif action == "premium":
        await query.message.reply_text(
            f"💎 Premium — 5 USDT\n\n"
            f"Binance Pay ID: {BINANCE_PAY_ID}\n"
            f"USDT Wallet: {USDT_WALLET}\n\n"
            "After payment send:\n/paid TXID"
        )

    elif action == "referral":
        link = f"https://t.me/YoutoolsPro_Bot?start={user_id}"
        await query.message.reply_text(f"🎁 Your referral link:\n{link}")

    elif action == "promo":
        await query.message.reply_text("🏷 Send your promo code")

    elif action == "support":
        await query.message.reply_text("🎟 Send your support message")


# =========================
# TEXT HANDLER
# =========================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()


    # ============ ADMIN TICKET REPLY ============
    reply_ticket_id = context.user_data.get("reply_ticket_id")

    if reply_ticket_id and user_id == ADMIN_ID:

        ticket = get_ticket(reply_ticket_id)

        if not ticket:
            await update.message.reply_text("❌ Ticket not found")
            context.user_data["reply_ticket_id"] = None
            return

        reply_ticket(reply_ticket_id, ADMIN_ID, text)

        try:
            await context.bot.send_message(
                chat_id=ticket.user_id,
                text=(
                    "📩 *Support Reply*\n\n"
                    f"{text}\n\n"
                    "— YouToolsPro Support"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            print("Send reply error:", e)

        await update.message.reply_text(f"✅ Reply sent for Ticket #{reply_ticket_id}")
        context.user_data["reply_ticket_id"] = None
        return


    # ============ ADMIN ACTION ============
    admin_action = context.user_data.get("admin_action")

    if admin_action and user_id == ADMIN_ID:

        if admin_action == "admin_grant":
            set_premium(int(text))
            await update.message.reply_text("✅ Premium granted")

        elif admin_action == "admin_revoke":
            revoke_premium(int(text))
            await update.message.reply_text("❌ Premium revoked")

        elif admin_action == "admin_ban":
            ban_user(int(text))
            await update.message.reply_text("🚫 User banned")

        elif admin_action == "admin_unban":
            unban_user(int(text))
            await update.message.reply_text("♻️ User unbanned")

        elif admin_action == "admin_broadcast":
            users = get_all_users()
            for u in users:
                try:
                    await context.bot.send_message(u.telegram_id, f"📢 {text}")
                except:
                    pass
            await update.message.reply_text("📢 Broadcast sent")

        context.user_data["admin_action"] = None
        return


    # ============ SUPPORT ============
    if context.user_data.get("tool") == "support":
        ticket = create_ticket(user_id, text)

        await context.bot.send_message(
            ADMIN_ID,
            f"🎟 Support Ticket #{ticket.id}\nUser: {user_id}\n\n{text}"
        )

        await update.message.reply_text("✅ Support ticket sent")
        context.user_data["tool"] = None
        return


    # ============ PROMO ============
    if context.user_data.get("tool") == "promo":
        promo = get_promo(text)

        if not promo:
            await update.message.reply_text("❌ Invalid or expired promo code")
        else:
            set_premium(user_id, promo.days)
            await update.message.reply_text(f"🎉 Promo applied! Premium for {promo.days} days")

        context.user_data["tool"] = None
        return


    # ============ USER TOOLS ============
    tool = context.user_data.get("tool")
    if not tool:
        return

    await update.message.reply_text("⏳ Processing...")

    engine_map = {
        "keyword": keyword_generator,
        "title": title_generator,
        "seo": seo_analyzer,
        "rank": rank_tracker,
        "spy": competitor_spy,
        "thumbnail": thumbnail_ai,
        "viral": viral_ideas,
        "content": content_generator,
        "trending": trending_videos,
        "growth": growth_mentor,
    }

    result = engine_map[tool](text)

    log_tool_usage(user_id, tool, text)

    pdf_file = generate_pdf(user_id, tool, result)

    await update.message.reply_text(result)
    await context.bot.send_document(user_id, document=open(pdf_file, "rb"), filename="YouToolsPro_Report.pdf")

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
        await update.message.reply_text("❌ Invalid transaction.")
        return

    set_premium(user_id)
    log_payment(user_id, txid, 5, "success")

    await update.message.reply_text("✅ Premium activated!")


# =========================
# BALANCE
# =========================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(update.effective_user.id)
    await update.message.reply_text(f"Wallet: {user.wallet} USDT")


# =========================
# PROMO COMMAND
# =========================

async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏷 Open dashboard → Promo Code")