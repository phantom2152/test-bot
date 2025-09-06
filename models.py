from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AccessToken(Base):
    __tablename__ = "access_tokens"

    telegram_id: Mapped[int] = mapped_column(primary_key=True)

    token: Mapped[str] = mapped_column(String(512), nullable=False)

    def __repr__(self) -> str:
        return f"AccessToken(telegram_id={self.telegram_id!r}, token={self.token!r})"
