import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import TURSO_DATABASE_URL, TURSO_AUTH_TOKEN

# Create engine for Turso (libsql)
engine = create_engine(
    f"sqlite+{TURSO_DATABASE_URL}?secure=true",
    connect_args={"auth_token": TURSO_AUTH_TOKEN},
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
