from datetime import datetime
from http import HTTPStatus
from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from telegram import Update

from config import SECRET_TOKEN
from bot import ptb
from utils.logger import logger


router = APIRouter()


@router.get("/health")
async def health_check():
    return JSONResponse({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'message': 'Bot is awake and running'
    })


@router.get("/ping")
async def ping():
    return Response(content='pong', media_type='text/plain')


@router.get("/", response_class=HTMLResponse)
@router.head("/")
async def home():
    html_content = f"""
    <html>
        <head><title>Telegram Bot Status</title></head>
        <body>
            <h1>🤖 Telegram Bot Status</h1>
            <p>Status: Active</p>
            <p>Server Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.post("/webhook")
async def process_update(request: Request):
    try:
        telegram_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if telegram_token != SECRET_TOKEN:
            logger.warning("Invalid secret token in webhook request")
            return Response(status_code=HTTPStatus.UNAUTHORIZED)

        req = await request.json()
        update = Update.de_json(req, ptb.bot)
        await ptb.process_update(update)
        return Response(status_code=HTTPStatus.OK)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
