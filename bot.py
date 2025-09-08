from telegram.ext import Application
from config import TOKEN, ENVIRONMENT

builder = (
    Application.builder().token(TOKEN).read_timeout(7).get_updates_read_timeout(42)
)

if ENVIRONMENT != "dev":
    builder = builder.updater(None)

ptb = builder.build()
