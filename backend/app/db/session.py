from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)

def get_db_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session

def check_database_connection() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

def close_database_connection() -> None:
    engine.dispose()