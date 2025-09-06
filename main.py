import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from http import HTTPStatus

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8000))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Initialize telegram application
ptb = (
    Application.builder()
    .updater(None)
    .token(TOKEN)
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Set webhook if WEBHOOK_URL is provided
    if WEBHOOK_URL:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        logger.info(f"Setting webhook to {webhook_url}")
        await ptb.bot.set_webhook(webhook_url)

    # Start the telegram application
    async with ptb:
        await ptb.start()
        logger.info("Telegram bot started")
        yield
        logger.info("Shutting down telegram bot")
        await ptb.stop()

# Initialize FastAPI app
app = FastAPI(
    title="Telegram Bot with Health Checks",
    description="A Telegram bot with health check endpoints for warming up cold starts",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint to wake up the app"""
    return JSONResponse({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'message': 'Bot is awake and running'
    })


@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return Response(content='pong', media_type='text/plain')


@app.get("/", response_class=HTMLResponse)
@app.head("/")
async def home():
    """Simple home page"""
    html_content = f'''
    <!DOCTYPE html>
    <html>
        <head>
            <title>Telegram Bot Status</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .status {{ color: green; font-weight: bold; }}
                code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>🤖 Telegram Bot Status</h1>
            <p class="status">Status: Active</p>
            <p>Server Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
            <p>Available endpoints:</p>
            <ul>
                <li><code>/health</code> - JSON health check</li>
                <li><code>/ping</code> - Simple ping response</li>
                <li><code>/webhook</code> - Telegram webhook endpoint</li>
            </ul>
            <p><strong>Use /health or /ping to warm up the app before sending messages to the bot.</strong></p>
        </body>
    </html>
    '''
    return HTMLResponse(content=html_content)


@app.post("/webhook")
async def process_update(request: Request):
    """Process incoming webhook from Telegram"""
    try:
        req = await request.json()
        update = Update.de_json(req, ptb.bot)
        await ptb.process_update(update)
        return Response(status_code=HTTPStatus.OK)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

# Telegram Bot Handlers


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(f"Hi {user.mention_html()}!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

# Add handlers to the application
ptb.add_handler(CommandHandler("start", start))
ptb.add_handler(CommandHandler("help", help_command))
ptb.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

if __name__ == "__main__":
    import uvicorn

    if WEBHOOK_URL:
        logger.info(f"Starting webhook mode on port {PORT}")
        logger.info(f"Webhook URL: {WEBHOOK_URL}/webhook")
    else:
        logger.info("Starting in development mode - webhook not set")

    uvicorn.run(app, host="0.0.0.0", port=PORT)
