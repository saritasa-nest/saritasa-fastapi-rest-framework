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
async def test_delete_api(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test delete API."""
    response = await api_client_factory(user).delete(
        lazy_url(action_name="delete", pk=test_model.id),
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return

    fastapi_rest_framework.testing.validate_no_content(response)
    assert not await repository.fetch_first(id=test_model.id)


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest.lazy_fixtures("user_jwt_data"),
    ],
)
async def test_delete_api_not_found(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test delete API when instance not found."""
    response = await api_client_factory(user).delete(
        lazy_url(action_name="delete", pk=-1),
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
async def test_soft_delete_api(
    soft_delete_test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    soft_delete_repository: example_app.repositories.SoftDeleteTestModelRepository,  # noqa: E501
    soft_delete_test_model: example_app.models.SoftDeleteTestModel,
) -> None:
    """Test soft delete API with soft-delete repository.

    Instance should be present in db with filled deleted field.

    """
    response = await api_client_factory(user).delete(
        soft_delete_test_model_lazy_url(
            action_name="delete",
            pk=soft_delete_test_model.id,
        ),
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return

    fastapi_rest_framework.testing.validate_no_content(response)
    assert (
        instance := await soft_delete_repository.fetch_first(
            id=soft_delete_test_model.id,
        )
    )
    assert instance.deleted, instance
