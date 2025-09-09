from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from cuid2 import cuid_wrapper
from datetime import datetime
from sqlalchemy import DateTime

make_cuid = cuid_wrapper()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_cuid)

    telegram_id: Mapped[int] = mapped_column(nullable=False, unique=True)

    telegram_username: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )

    def __repr__(self) -> str:
        return (
            f"id(cuid={self.id!r}, "
            f"telegram_id={self.telegram_id!r}, "
            f"telegram_username={self.seedr_username!r}, "
            f"created_at={self.created_at!r})"
        )
