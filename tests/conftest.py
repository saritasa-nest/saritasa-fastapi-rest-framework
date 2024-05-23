import collections.abc
import functools

import fastapi
import pytest
import saritasa_s3_tools
import saritasa_sqlalchemy_tools

import example_app
import example_app.dependencies
import fastapi_rest_framework

from . import factories, shortcuts


@pytest.fixture(scope="session", autouse=True)
def anyio_backend() -> str:
    """Specify async backend."""
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def _adjust_s3_factories(
    s3_bucket_name: str,
) -> None:
    """Adjust buckets for factories."""
    factories.S3ImageFactory.bucket = s3_bucket_name


@pytest.fixture(scope="session")
def manual_database_setup() -> collections.abc.Callable[..., None]:
    """Return callable object that will be called to init database."""
    return saritasa_sqlalchemy_tools.BaseModel.metadata.create_all


@pytest.fixture
async def test_model(
    db_session: saritasa_sqlalchemy_tools.Session,
) -> example_app.models.TestModel:
    """Generate test_model instance."""
    test_model = await factories.TestModelFactory.create_async(
        session=db_session,
    )
    test_model.m2m_related_models_ids = []  # type: ignore
    return test_model


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
def token_factory() -> collections.abc.Callable[[shortcuts.UserData], str]:
    """Get factory for generating jwt token."""
    return lambda user: example_app.security.JWTAuth.generate_jwt_for_user(
        user=user,
    )


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
    fastapi_app: fastapi.FastAPI,
    db_session_dependency: saritasa_sqlalchemy_tools.SessionFactory,
    async_s3_client: saritasa_s3_tools.AsyncS3Client,
) -> fastapi.FastAPI:
    """Override app dependencies."""
    fastapi_app.dependency_overrides[example_app.db.get_db_session] = (
        db_session_dependency
    )
    fastapi_app.dependency_overrides[
        example_app.dependencies.get_s3_client
    ] = lambda: async_s3_client

    return fastapi_app


@pytest.fixture
def user_jwt_data() -> shortcuts.UserData:
    """Generate test JWT data for default user."""
    return factories.UserJWTDataFactory()  # type: ignore


@pytest.fixture(scope="session")
def view() -> type[fastapi_rest_framework.views.AnyBaseAPIView]:
    """Get view for lazy_url."""
    return example_app.views.TestModelAPIView


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
