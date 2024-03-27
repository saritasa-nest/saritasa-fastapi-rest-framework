import collections.abc

import saritasa_sqlalchemy_tools


async def get_db_session() -> (
    collections.abc.AsyncIterator[saritasa_sqlalchemy_tools.Session]
):
    """Set up and get db session."""
    async with saritasa_sqlalchemy_tools.get_async_session_factory(
        drivername="postgresql+asyncpg",
        username="fastapi-rest-framework-user",
        password="manager",  # noqa: S106
        host="postgres",
        port=5432,
        database="fastapi-rest-framework-user-dev",
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        on_connect=[],
        query={},
    )() as session:
        try:
            yield session
        except Exception as error:
            await session.rollback()
            raise error
        else:
            await session.commit()
