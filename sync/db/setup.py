from pathlib import Path
from sqlite3 import Connection
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from ..strings import normalize_cyrillic


async def setup_database(
    database: str | Path,
    session_factory: async_sessionmaker[AsyncSession]
) -> None:
    # Validate the database path
    db_path = _validate_database_path(database)

    # Create an engine
    engine = _create_engine(db_path)

    # Configure the engine
    _configure_engine(engine)
    session_factory.configure(bind=engine)

    # Initialize the database
    try:
        await _initialize_database(engine)
    except Exception as exc:
        raise ValueError(f"Failed to initialize the database {database!r}: {exc}") from exc



def _validate_database_path(database: str | Path) -> Path:
    if not database:
        raise ValueError(f"Database path {database!r} is empty")

    db_path = Path(database).resolve()

    if db_path.is_dir():
        raise ValueError(f"Database path {database!r} is a directory")

    return db_path


def _create_engine(db_path: Path) -> AsyncEngine:
    db_url = f"sqlite+aiosqlite:///{db_path}"

    return create_async_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False}
    )


def _configure_engine(engine: AsyncEngine) -> None:
    event.listen(
        engine.sync_engine,
        "connect",
        _register_sqlite_functions
    )


def _register_sqlite_functions(dbapi_connection: Connection, row: tuple[Any]) -> None:
    dbapi_connection.create_function("normalize_cyrillic", 1, normalize_cyrillic)


async def _initialize_database(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


__all__ = ["setup_database"]
