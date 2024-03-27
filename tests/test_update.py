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
async def test_update_api(
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test create API."""
    schema = example_app.views.TestModelAPIView.update_schema.model_validate(
        test_model,
    )
    schema.text = "Test"
    response = await auth_api_client_factory(user).put(
        test_model_lazy_url(action_name="update", pk=test_model.id),
        json=schema.model_dump(mode="json"),
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
    assert (instance := await repository.fetch_first(id=response_data.id))
    assert instance.text == schema.text


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest.lazy_fixtures("user_jwt_data"),
    ],
)
async def test_update_api_not_found(
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test update API when instance not found."""
    response = await auth_api_client_factory(user).put(
        test_model_lazy_url(action_name="update", pk=-1),
        json=example_app.views.TestModelAPIView.update_schema.model_validate(
            test_model,
        ).model_dump(mode="json"),
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return

    fastapi_rest_framework.testing.validate_not_found(response=response)


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest.lazy_fixtures("user_jwt_data"),
    ],
)
async def test_update_api_custom_detail_response(
    soft_delete_test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    soft_delete_repository: example_app.repositories.TestModelRepository,
    soft_delete_test_model: example_app.models.SoftDeleteTestModel,
) -> None:
    """Test update API with custom detail response."""
    response = await auth_api_client_factory(user).put(
        soft_delete_test_model_lazy_url(
            action_name="update",
            pk=soft_delete_test_model.id,
        ),
        json=example_app.views.SoftDeleteTestModelAPIView.create_schema.model_validate(
            soft_delete_test_model,
        ).model_dump(mode="json"),
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return

    response_data = fastapi_rest_framework.testing.extract_schema_from_response(  # noqa: E501
        response=response,
        schema=example_app.views.SoftDeleteTestModelAPIView.update_detail_schema,
    )
    assert await soft_delete_repository.exists(id=response_data.id)
    assert response_data.modified
    assert not hasattr(response_data, "created")
