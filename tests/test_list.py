import pytest

import example_app
import fastapi_rest_framework

from . import shortcuts


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest.lazy_fixtures("user_jwt_data"),
    ],
)
async def test_list_api(
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model_list: list[example_app.models.TestModel],
) -> None:
    """Test list API."""
    response = await auth_api_client_factory(user).get(
        test_model_lazy_url(action_name="list"),
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return

    response_data = (
        fastapi_rest_framework.testing.extract_paginated_result_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.list_schema,
        )
    )
    assert response_data.count == len(test_model_list), response_data
