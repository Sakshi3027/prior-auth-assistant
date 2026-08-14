"""
Database connection setup. Reads DATABASE_URL from the environment and
creates a SQLAlchemy engine + session factory the rest of the app uses.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_session():
    """Yields a session and ensures it's closed. Used by the repository."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()