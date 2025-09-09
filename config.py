import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SECRET_TOKEN = os.getenv("WEBHOOK_SECRET")
PORT = int(os.getenv("PORT", 8000))


PSQL_USERNAME = os.getenv("PSQL_USERNAME")
PSQL_PASSWORD = os.getenv("PSQL_PASSWORD")
PSQL_URL = os.getenv("PSQL_URL")

ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")
