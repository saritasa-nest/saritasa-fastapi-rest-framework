import http

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
async def test_create_api(
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test create API."""
    response = await auth_api_client_factory(user).post(
        test_model_lazy_url(action_name="create"),
        json=example_app.views.TestModelAPIView.create_schema.model_validate(
            test_model,
        ).model_dump(mode="json"),
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return

    response_data = (
        fastapi_rest_framework.testing.extract_schema_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.detail_schema,
            expected_status=http.HTTPStatus.CREATED,
        )
    )
    assert await repository.exists(id=response_data.id)
