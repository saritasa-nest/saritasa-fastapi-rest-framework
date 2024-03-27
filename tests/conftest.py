import asyncio
import collections.abc
import datetime
import functools
import typing

import fastapi
import httpx
import jwt
import pytest
import saritasa_sqlalchemy_tools
import sqlalchemy

import example_app
import fastapi_rest_framework

from . import factories, shortcuts


@pytest.fixture(scope="session")
def event_loop() -> (
    collections.abc.Generator[
        asyncio.AbstractEventLoop,
        typing.Any,
        None,
    ]
):
    """Override `event_loop` fixture to change scope to `session`.

    Needed for pytest-async-sqlalchemy.

    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def database_url(request: pytest.FixtureRequest) -> str:
    """Override database url.

    Grab configs from settings and add support for pytest-xdist

    """
    worker_input = getattr(
        request.config,
        "workerinput",
        {
            "workerid": "",
        },
    )
    return sqlalchemy.engine.URL(
        drivername="postgresql+asyncpg",
        username="fastapi-rest-framework-user",
        password="manager",
        host="postgres",
        port=5432,
        database="_".join(
            filter(
                None,
                (
                    "fastapi-rest-framework-dev",
                    "test",
                    worker_input["workerid"],
                ),
            ),
        ),
        query={},  # type: ignore
    ).render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def init_database() -> collections.abc.Callable[..., None]:
    """Return callable object that will be called to init database.

    Overridden fixture from `pytest-async-sqlalchemy package`.
    https://github.com/igortg/pytest-async-sqlalchemy

    """
    return saritasa_sqlalchemy_tools.BaseModel.metadata.create_all


@pytest.fixture
async def test_model(
    db_session: saritasa_sqlalchemy_tools.Session,
) -> example_app.models.TestModel:
    """Generate test_model instance."""
    return await factories.TestModelFactory.create_async(session=db_session)


@pytest.fixture
async def related_model(
    db_session: saritasa_sqlalchemy_tools.Session,
) -> example_app.models.RelatedModel:
    """Generate test_model instance."""
    return await factories.RelatedModelFactory.create_async(session=db_session)


@pytest.fixture
async def test_model_list(
    db_session: saritasa_sqlalchemy_tools.Session,
) -> collections.abc.Sequence[example_app.models.TestModel]:
    """Generate test_model instances."""
    return await factories.TestModelFactory.create_batch_async(
        session=db_session,
        size=5,
    )


@pytest.fixture
async def repository(
    db_session: saritasa_sqlalchemy_tools.Session,
) -> example_app.repositories.TestModelRepository:
    """Get repository for `TestModel`."""
    return example_app.repositories.TestModelRepository(db_session=db_session)


@pytest.fixture
async def soft_delete_test_model(
    db_session: saritasa_sqlalchemy_tools.Session,
) -> example_app.models.SoftDeleteTestModel:
    """Generate `SoftDeleteTestModel` instance."""
    return await factories.SoftDeleteTestModelFactory.create_async(
        session=db_session,
    )


@pytest.fixture
async def soft_delete_repository(
    db_session: saritasa_sqlalchemy_tools.Session,
) -> example_app.repositories.SoftDeleteTestModelRepository:
    """Get soft delete repository."""
    return example_app.repositories.SoftDeleteTestModelRepository(
        db_session=db_session,
    )


@pytest.fixture(scope="session")
def jwt_factory() -> collections.abc.Callable[[shortcuts.UserData], str]:
    """Get factory for generating jwt token."""

    def _get_jwt(user: shortcuts.UserData) -> str:
        return jwt.encode(
            payload={
                "id": user.id,
                "allow": user.allow,
                "iat": datetime.datetime.now(datetime.UTC),
                "exp": (
                    datetime.datetime.now(datetime.UTC)
                    + datetime.timedelta(days=100)
                ),
            },
            key=example_app.security.jwt_private_key,
            algorithm=example_app.security.JWTAuth.jwt_algorithms[0],
        )

    return _get_jwt


@pytest.fixture
async def auth_api_client_factory(
    api_client: httpx.AsyncClient,
    jwt_factory: collections.abc.Callable[[shortcuts.UserData], str],
) -> shortcuts.AuthApiClientFactory:
    """Add token to a client."""

    def _auth_api_client_factory(
        user: shortcuts.UserData | None,
    ) -> httpx.AsyncClient:
        if user:
            api_client.headers["Authorization"] = f"Bearer {jwt_factory(user)}"
        api_client.user = user  # type: ignore
        return api_client

    return _auth_api_client_factory


@pytest.fixture
def db_session_dependency(
    db_session: saritasa_sqlalchemy_tools.Session,
) -> saritasa_sqlalchemy_tools.SessionFactory:
    """Prepare db session dependency override."""

    async def _get_db_override() -> (
        collections.abc.AsyncIterator[saritasa_sqlalchemy_tools.Session,]
    ):
        yield db_session

    return _get_db_override


@pytest.fixture
def fastapi_app(
    db_session_dependency: saritasa_sqlalchemy_tools.SessionFactory,
) -> fastapi.FastAPI:
    """Override app dependencies."""
    example_app.fastapi_app.dependency_overrides[
        example_app.db.get_db_session
    ] = db_session_dependency

    return example_app.fastapi_app


@pytest.fixture
async def api_client(
    fastapi_app: fastapi.FastAPI,
) -> collections.abc.AsyncGenerator[httpx.AsyncClient, None]:
    """Fixture for test api client to make requests."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=fastapi_app),  # type: ignore
        # This is needed, so won't need to write full url in tests
        base_url="http://testapp",
    ) as client:
        yield client


@pytest.fixture
def user_jwt_data() -> shortcuts.UserData:
    """Generate test JWT data for default user."""
    return factories.UserJWTDataFactory()  # type: ignore


@pytest.fixture
def test_model_lazy_url(
    fastapi_app: fastapi.FastAPI,
) -> fastapi_rest_framework.testing.LazyUrl:
    """Generate shortcut to lazy urls."""
    return functools.partial(
        fastapi_rest_framework.testing.lazy_url,
        app=fastapi_app,
        view=example_app.views.TestModelAPIView,
    )


@pytest.fixture
def soft_delete_test_model_lazy_url(
    fastapi_app: fastapi.FastAPI,
) -> fastapi_rest_framework.testing.LazyUrl:
    """Generate shortcut to lazy urls."""
    return functools.partial(
        fastapi_rest_framework.testing.lazy_url,
        app=fastapi_app,
        view=example_app.views.SoftDeleteTestModelAPIView,
    )
