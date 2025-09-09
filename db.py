from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import PSQL_PASSWORD, PSQL_URL, PSQL_USERNAME

# Create engine for Cockroachdb
engine = create_engine(
    f"cockroachdb://{PSQL_USERNAME}:{PSQL_PASSWORD}@{PSQL_URL}",
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
