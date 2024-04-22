import collections.abc
import functools
import importlib
import typing

import fastapi
import httpx
import pytest

from .. import permissions, views
from . import tools, types


def pytest_addoption(parser: pytest.Parser) -> None:
    """Set up cmd args and ini options."""
    parser.addini(
        "fastapi_app_path",
        "Path for fastapi app instance.",
    )
    parser.addini(
        "fastapi_auth_header_name",
        "Auth header name",
        default="Authorization",
    )
    parser.addini(
        "fastapi_auth_header_value_template",
        "Template for auth header value.",
        default="Bearer {token}",
    )


@pytest.fixture
def fastapi_app(
    request: pytest.FixtureRequest,
) -> fastapi.FastAPI:
    """Get fastapi app."""
    app_path = str(request.config.inicfg.get("fastapi_app_path"))
    if not app_path:
        raise ValueError(  # pragma: no cover
            "Please specify path to fastapi app "
            "via `fastapi_app_path` ini setting.",
        )
    *module, app = app_path.split(".")
    return getattr(importlib.import_module(".".join(module)), app)


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
def token_factory() -> collections.abc.Callable[[typing.Any], str]:  # noqa: PT004
    """Get factory for generating token."""
    raise NotImplementedError(  # pragma: no cover
        "Please implement `token_factory` fixture, "
        "if you wish to use `api_client_factory`!",
    )


@pytest.fixture
async def api_client_factory(
    request: pytest.FixtureRequest,
    api_client: httpx.AsyncClient,
    token_factory: collections.abc.Callable[[permissions.UserT], str],
) -> types.AuthApiClientFactory[permissions.UserT]:
    """Add token to a client."""

    def _auth_api_client_factory(
        user: permissions.UserT | None,
    ) -> httpx.AsyncClient:
        if user:
            api_client.headers[
                str(
                    request.config.inicfg.get(
                        "fastapi_auth_header_name",
                        "Authorization",
                    ),
                )
            ] = str(
                request.config.inicfg.get(
                    "fastapi_auth_header_value_template",
                    "Bearer {token}",
                ),
            ).format(
                token=token_factory(user),
            )
        api_client.user = user  # type: ignore
        return api_client

    return _auth_api_client_factory


@pytest.fixture
def view() -> type[views.AnyBaseAPIView]:  # noqa: PT004
    """Get view for lazy_url."""
    raise NotImplementedError(  # pragma: no cover
        "Please implement `view` fixture, if you wish to use `lazy_url`!",
    )


@pytest.fixture
def lazy_url(
    fastapi_app: fastapi.FastAPI,
    view: type[views.AnyBaseAPIView],
) -> types.LazyUrl:
    """Generate shortcut to lazy urls."""
    return functools.partial(
        tools.lazy_url,
        app=fastapi_app,
        view=view,
    )
