import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from bot import ptb

from config import WEBHOOK_URL, SECRET_TOKEN
from handlers import register_handlers
from routes import router
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:

        if not WEBHOOK_URL or not SECRET_TOKEN:
            logger.critical(
                "❌ Missing required environment variables: "
                "WEBHOOK_URL and/or WEBHOOK_SECRET. "
                "The app cannot start without them!"
            )
            sys.exit(1)

        webhook_url = f"{WEBHOOK_URL.strip().rstrip('/')}/webhook"

        try:
            logger.info(f"Setting webhook to {webhook_url}")
            result = await ptb.bot.set_webhook(
                webhook_url, secret_token=SECRET_TOKEN, drop_pending_updates=True
            )
            logger.info(f"✅ Webhook set result: {result}")
        except Exception as e:
            logger.critical(f"❌ Failed to set webhook: {e}")
            sys.exit(1)

        async with ptb:
            try:
                await ptb.start()
                logger.info("✅ Telegram bot started in webhook mode")
                yield
            except Exception as e:
                logger.critical(f"❌ Failed to start Telegram bot: {e}")
                sys.exit(1)
            finally:
                logger.info("🔻 Shutting down telegram bot")
                await ptb.stop()

    except Exception as e:
        logger.critical(f"❌ Unexpected error during startup: {e}")
        sys.exit(1)


# Register all commands
register_handlers(ptb)

app = FastAPI(
    title="Telegram Bot with Health Checks",
    description="A Telegram bot with health check endpoints",
    lifespan=lifespan,
)

app.include_router(router)
