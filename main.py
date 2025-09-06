import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from config import WEBHOOK_URL, SECRET_TOKEN
from bot import ptb
from handlers import register_handlers
from routes import router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if WEBHOOK_URL and SECRET_TOKEN:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        logger.info(f"Setting webhook to {webhook_url}")
        await ptb.bot.set_webhook(webhook_url, secret_token=SECRET_TOKEN)

    async with ptb:
        await ptb.start()
        logger.info("Telegram bot started")
        yield
        logger.info("Shutting down telegram bot")
        await ptb.stop()

app = FastAPI(
    title="Telegram Bot with Health Checks",
    description="A Telegram bot with health check endpoints",
    lifespan=lifespan
)

# Register routes
app.include_router(router)

# Register Telegram handlers
register_handlers(ptb)
