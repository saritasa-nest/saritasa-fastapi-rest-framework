import pytest
import pytest_lazy_fixtures

import example_app
import fastapi_rest_framework

from . import factories, shortcuts


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest_lazy_fixtures.lf("user_jwt_data"),
    ],
)
async def test_paginated_action_api(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model_list: list[example_app.models.TestModel],
) -> None:
    """Test paginated action api endpoint."""
    response = await api_client_factory(user).get(
        lazy_url(action_name="paginated-action"),
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


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest_lazy_fixtures.lf("user_jwt_data"),
    ],
)
async def test_action_api(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
    test_model_list: list[example_app.models.TestModel],
) -> None:
    """Test action api endpoint."""
    update_schema = (
        example_app.schemas.TestModelBulkCreateRequest.model_validate(
            test_model,
        )
    )
    update_schema.text = "TextUnique"
    update_schema.text_unique = "TextUnique"
    test_model_not_saved = await factories.TestModelFactory.create_async(
        repository.db_session,
    )
    create_schema = (
        example_app.schemas.TestModelBulkCreateRequest.model_validate(
            test_model_not_saved,
        )
    )
    create_schema.text = "TextUnique1"
    create_schema.text_unique = "TextUnique1"
    response = await api_client_factory(user).post(
        lazy_url(action_name="action"),
        json=[
            create_schema.model_dump(mode="json"),
            update_schema.model_dump(mode="json"),
        ],
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return

    fastapi_rest_framework.testing.validate_no_content(response)
    assert await repository.count() == 2


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest_lazy_fixtures.lf("user_jwt_data"),
    ],
)
async def test_action_detail_api(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test detail action api endpoint."""
    response = await api_client_factory(user).put(
        lazy_url(
            action_name="action-detail",
            pk=test_model.id,
        ),
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return
    fastapi_rest_framework.testing.validate_no_content(response)
    assert (instance := await repository.fetch_first(id=test_model.id))
    assert instance.text_unique == "text_unique_action_detail"


async def test_action_detail_api_not_found(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test detail action api endpoint when instance is not found."""
    response = await api_client_factory(user_jwt_data).put(
        lazy_url(
            action_name="action-detail",
            pk=-1,
        ),
    )
    fastapi_rest_framework.testing.validate_not_found(response)
