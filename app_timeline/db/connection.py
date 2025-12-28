"""
app_timeline.db.connection

Database connection management utilities.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import get_config

# Global engine instance
_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def get_engine(echo: Optional[bool] = None) -> Engine:
    """
    Get the SQLAlchemy engine (singleton pattern).

    :param echo: Optional override for SQL echo setting
    :return: SQLAlchemy Engine instance
    """
    global _engine

    if _engine is None:
        config = get_config()
        connection_string = config.database.connection_string
        echo_sql = echo if echo is not None else config.database.echo

        # Ensure database directory exists
        if config.database.dialect == "sqlite":
            db_path = Path(config.database.path)
            db_path.parent.mkdir(parents=True, exist_ok=True)

        _engine = create_engine(connection_string, echo=echo_sql)

    return _engine


def get_session_factory() -> sessionmaker:
    """
    Get the session factory (singleton pattern).

    :return: SQLAlchemy sessionmaker
    """
    global _session_factory

    if _session_factory is None:
        engine = get_engine()
        _session_factory = sessionmaker(bind=engine)

    return _session_factory


def get_session() -> Session:
    """
    Create a new database session.

    :return: SQLAlchemy Session instance
    """
    factory = get_session_factory()
    return factory()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    This is a convenience function that imports all models and creates tables.
    """
    from ..models import Base

    engine = get_engine()
    Base.metadata.create_all(engine)


def reset_engine() -> None:
    """
    Reset the global engine and session factory (useful for testing).
    """
    global _engine, _session_factory
    _engine = None
    _session_factory = None
