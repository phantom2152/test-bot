import logging
from telegram.ext import Application

from config import TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

ptb = (
    Application.builder()
    .updater(None)
    .token(TOKEN)
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)
