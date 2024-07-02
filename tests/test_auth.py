import example_app
import fastapi_rest_framework

from . import factories, shortcuts


async def test_refresh_token_cannot_be_used_as_access(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    test_model: example_app.models.TestModel,
    api_client_factory: shortcuts.AuthApiClientFactory,
) -> None:
    """Ensure that JWT `refresh` token cannot be used as `access` token."""
    api_client = api_client_factory(
        factories.UserJWTDataFactory(
            token_type=fastapi_rest_framework.jwt.TokenType.refresh,
        ),
    )
    response = await api_client.get(
        lazy_url(action_name="detail", pk=test_model.id),
    )
    fastapi_rest_framework.testing.validate_unauthorized(
        response=response,
        message=(
            f"Token type must be {fastapi_rest_framework.jwt.TokenType.access}"
        ),
    )
