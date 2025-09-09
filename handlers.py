from repository.user import get_or_create_user
from utils.logger import logger
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        get_or_create_user(user.id, user.username)
        await update.message.reply_html(f"Hi {user.mention_html()}!")
    except Exception as e:
        logger.exception("Error while creating user record")
        await update.message.reply_html(
            f"Hi {user.mention_html()} the bot is experiencing some issues, please try again!"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help lol!")


def register_handlers(ptb):
    ptb.add_handler(CommandHandler("start", start))
    ptb.add_handler(CommandHandler("help", help_command))
