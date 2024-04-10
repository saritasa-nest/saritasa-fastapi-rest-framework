import http

import pytest

import example_app
import fastapi_rest_framework

from . import shortcuts


async def test_permission_for_action_api(
    soft_delete_test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    soft_delete_repository: example_app.repositories.SoftDeleteTestModelRepository,  # noqa: E501
    soft_delete_test_model: example_app.models.SoftDeleteTestModel,
) -> None:
    """Test permission setting for specific action."""
    user_jwt_data.allow = False
    response = await auth_api_client_factory(user_jwt_data).delete(
        soft_delete_test_model_lazy_url(
            action_name="delete",
            pk=soft_delete_test_model.id,
        ),
    )
    error = (
        fastapi_rest_framework.testing.extract_general_errors_from_response(
            response,
            expected_status=http.HTTPStatus.FORBIDDEN,
        )
    )
    assert error.detail == "User is not allowed", error


async def test_default_permission(
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test detail API."""
    user_jwt_data.allow = False
    response = await auth_api_client_factory(user_jwt_data).get(
        test_model_lazy_url(action_name="detail", pk=test_model.id),
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return

    error = (
        fastapi_rest_framework.testing.extract_general_errors_from_response(
            response,
            expected_status=http.HTTPStatus.FORBIDDEN,
        )
    )
    assert error.detail == "User is not allowed", error


@pytest.mark.parametrize(
    "allow",
    [
        True,
        False,
    ],
)
async def test_default_permission_dependency(
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    allow: bool,
) -> None:
    """Test endpoint get_permissions_dependency."""
    user_jwt_data.allow = allow
    response = await auth_api_client_factory(user_jwt_data).get(
        "/guarded-endpoint/",
    )
    if allow:
        assert response.status_code == http.HTTPStatus.OK
        return
    error = (
        fastapi_rest_framework.testing.extract_general_errors_from_response(
            response,
            expected_status=http.HTTPStatus.FORBIDDEN,
        )
    )
    assert error.detail == "User is not allowed", error
