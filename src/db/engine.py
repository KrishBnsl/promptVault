"""SQLAlchemy engine and session management."""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def _create_engine() -> Engine:
    return create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )


engine = _create_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def configure_db(db_path: str) -> None:
    """Reconfigure the process-wide engine before opening any sessions."""
    global engine

    engine.dispose()
    settings.db_path = db_path
    engine = _create_engine()
    SessionLocal.configure(bind=engine)


def init_db() -> None:
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
