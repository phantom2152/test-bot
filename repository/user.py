from sqlalchemy.dialects.postgresql import insert

from db import SessionLocal
from models import User


def get_or_create_user(telegram_id: int, telegram_username: str | None = None):
    """Insert user if missing; no-op if already exists."""
    with SessionLocal() as db:
        stmt = (
            insert(User)
            .values(telegram_id=telegram_id, telegram_username=telegram_username)
            .on_conflict_do_nothing(index_elements=[User.telegram_id])
        )
        db.execute(stmt)
        db.commit()
