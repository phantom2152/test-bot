# common.py
from bot import ptb
from handlers import register_handlers
from models import Base
from db import engine
from utils.logger import logger


def init_bot_and_db():
    """Register bot handlers and ensure DB tables exist."""
    register_handlers(ptb)

    try:
        logger.info("Ensuring database tables exist...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database ready")
    except Exception as e:
        logger.critical(f"❌ Failed to initialize database: {e}")
        raise

    return ptb
