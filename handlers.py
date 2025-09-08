from db import SessionLocal
from utils.logger import logger
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from seedrcc import AsyncSeedr, Token
from models import AccessToken


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(f"Hi {user.mention_html()}!")


async def link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    db = SessionLocal()

    try:
        existing = db.get(AccessToken, telegram_id)
        if existing:
            await update.message.reply_text("You are already registerd")
            return

        codes = await AsyncSeedr.get_device_code()
        # Create a button
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔗 Link Account", callback_data=f"link_account:{codes.device_code}"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send message with button
        await update.message.reply_text(
            "Hi, in order to link your Seedr account copy the below code:\n\n"
            f"Please open this URL in your browser: {codes.verification_url}"
            f"**And enter this code**: `{codes.user_code}`\n\n",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.error("Error while linking account")
        await update.message.reply_text("Something is broken from our side")

    finally:
        db.close()


async def account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    db = SessionLocal()

    try:
        existing = db.get(AccessToken, telegram_id)

        if not existing:
            await update.message.reply_text(
                "You are not registerd" "Please use /link to connect your seedr account"
            )

    except Exception as e:
        pass


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help lol!")


# ✅ Callback handler for button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = SessionLocal()
    query = update.callback_query
    telegram_id = update.effective_user.id
    await query.answer()  # Acknowledge the button press
    data = query.data

    action, device_code = data.split(":", 1)
    if action == "link_account":

        try:

            client = await AsyncSeedr.from_device_code(device_code)

            async with client:
                settings = await client.get_settings()
                message = f"Success! Hello, {settings.account.username}"

                token = client.token
                base64_token = token.to_base64()

                db.add(AccessToken(telegram_id=telegram_id, token=base64_token))

                db.commit()
        except Exception as e:
            logger.error(f"Error while adding token to db: {e}")
            message = "SOrry there was error while connexting db"

        finally:
            db.close()

        await query.edit_message_text(message)  # Replace message with confirmation


def register_handlers(ptb):
    ptb.add_handler(CommandHandler("start", start))
    ptb.add_handler(CommandHandler("help", help_command))
    ptb.add_handler(CommandHandler("link", link))
    ptb.add_handler(CallbackQueryHandler(button_handler))
