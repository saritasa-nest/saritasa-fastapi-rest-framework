import contextlib

import pytest

import fastapi_rest_framework

from . import shortcuts


@pytest.fixture
def jwt_authentication() -> shortcuts.JWTAuthenticationType:
    """Get instance of `JWTTokenAuthentication`."""
    return shortcuts.JWTAuthentication


@pytest.fixture
def jwt_access_token(
    user_jwt_data: shortcuts.UserData,
    jwt_authentication: shortcuts.JWTAuthenticationType,
) -> str:
    """Generate JWT access token."""
    return jwt_authentication.generate_jwt_for_user(user=user_jwt_data)


@pytest.fixture
def jwt_refresh_data(
    user_jwt_data: shortcuts.UserData,
) -> shortcuts.UserData:
    """Generate test JWT data for refresh token."""
    user_jwt_data.token_type = fastapi_rest_framework.jwt.TokenType.refresh
    return user_jwt_data


@pytest.fixture
def jwt_refresh_token(
    jwt_refresh_data: shortcuts.UserData,
    jwt_authentication: shortcuts.JWTAuthenticationType,
) -> str:
    """Generate JWT refresh token."""
    return jwt_authentication.generate_jwt_for_user(
        user=jwt_refresh_data,
    )


def test_refresh_token_cannot_be_used_as_access(
    jwt_authentication: shortcuts.JWTAuthenticationType,
    jwt_refresh_token: str,
) -> None:
    """Ensure that JWT `refresh` token cannot be used as `access` token."""
    with contextlib.suppress(fastapi_rest_framework.UnauthorizedException):
        jwt_authentication.decode_access(token=jwt_refresh_token)
