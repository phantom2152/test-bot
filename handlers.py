from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(f"Hi {user.mention_html()}!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


def register_handlers(ptb):
    ptb.add_handler(CommandHandler("start", start))
    ptb.add_handler(CommandHandler("help", help_command))
    ptb.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
