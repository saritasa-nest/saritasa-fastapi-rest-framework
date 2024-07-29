import pytest
import pytest_lazy_fixtures

import example_app
import fastapi_rest_framework

from . import shortcuts


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest_lazy_fixtures.lf("user_jwt_data"),
    ],
)
async def test_detail_api(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test detail API."""
    response = await api_client_factory(user).get(
        lazy_url(action_name="detail", pk=test_model.id),
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return

    response_data = (
        fastapi_rest_framework.testing.extract_schema_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.detail_schema,
        )
    )
    assert response_data.id == test_model.id, response_data


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest_lazy_fixtures.lf("user_jwt_data"),
    ],
)
async def test_detail_api_not_found(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test detail API when instance not found."""
    response = await api_client_factory(user).get(
        lazy_url(action_name="detail", pk=-1),
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return

    fastapi_rest_framework.testing.validate_not_found(response=response)
