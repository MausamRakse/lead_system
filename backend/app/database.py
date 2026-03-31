from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from typing import Generator
from app.config import settings

connect_args = {"sslmode": "require"} if settings.DATABASE_URL.startswith("postgresql") else {}

# Use NullPool when connecting to a dedicated connection pooler like Supavisor (Port 6543)
engine = create_engine(
    settings.DATABASE_URL, 
    echo=False, 
    connect_args=connect_args,
    poolclass=NullPool
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
