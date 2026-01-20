import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from handlers import (
    start,
    paid,
    promo,
    balance,
    button_handler,
    handle_user_input,
    admin
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing")

telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("paid", paid))
telegram_app.add_handler(CommandHandler("promo", promo))
telegram_app.add_handler(CommandHandler("balance", balance))
telegram_app.add_handler(CommandHandler("admin", admin))

telegram_app.add_handler(CallbackQueryHandler(button_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))