import collections.abc

import saritasa_sqlalchemy_tools

db_session_manager = saritasa_sqlalchemy_tools.get_async_db_session(
    drivername="postgresql+asyncpg",
    username="fastapi-rest-framework-user",
    password="manager",  # noqa: S106
    host="postgres",
    port=5432,
    database="fastapi-rest-framework-dev",
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    on_connect=[],
    query={},
)


async def get_db_session() -> (
    collections.abc.AsyncIterator[saritasa_sqlalchemy_tools.Session]
):
    """Set up and get db session."""
    async with db_session_manager as session:
        yield session
