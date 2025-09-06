import logging
import os
from dotenv import load_dotenv
from datetime import datetime
import json

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from tornado.web import RequestHandler

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8000))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class HealthHandler(RequestHandler):
    """Health check endpoint handler"""
    def get(self):
        self.set_header("Content-Type", "application/json")
        response = {
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'message': 'Bot is awake and running'
        }
        self.write(json.dumps(response))

class PingHandler(RequestHandler):
    """Simple ping endpoint handler"""
    def get(self):
        self.set_header("Content-Type", "text/plain")
        self.write('pong')

class HomeHandler(RequestHandler):
    """Simple home page handler"""
    def get(self):
        self.set_header("Content-Type", "text/html")
        html = f'''
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
                </ul>
                <p><strong>Use these endpoints to warm up the app before sending messages to the bot.</strong></p>
            </body>
        </html>
        '''
        self.write(html)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, echo))

    if WEBHOOK_URL:
        # Production mode - use webhooks
        logger.info(f"Starting webhook on {WEBHOOK_URL} on port {PORT}")
        
        # Create custom web app with health check endpoints
        # This uses the built-in tornado server from python-telegram-bot
        from tornado.web import Application as TornadoApp
        
        web_app = TornadoApp([
            (r"/", HomeHandler),
            (r"/health", HealthHandler),
            (r"/ping", PingHandler),
        ])
        
        application.run_webhook(
            listen='0.0.0.0',
            port=PORT,
            webhook_url=WEBHOOK_URL,
            web_app=web_app  # This adds our custom endpoints to the webhook server
        )
    else:
        # Development mode - use polling
        logger.info("Starting in polling mode")
        application.run_polling()

if __name__ == "__main__":
    main()
