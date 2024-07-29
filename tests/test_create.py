import http

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
async def test_create_api(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test create API."""
    test_model.m2m_related_models_ids = [
        (
            await factories.RelatedModelFactory.create_async(
                repository.db_session,
            )
        ).id,
        (
            await factories.RelatedModelFactory.create_async(
                repository.db_session,
            )
        ).id,
    ]
    schema = example_app.views.TestModelAPIView.create_schema.model_validate(
        test_model,
    )
    schema.text_unique = "TextUnique"
    schema.text_nullable = "TestValue"
    response = await api_client_factory(user).post(
        lazy_url(action_name="create"),
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
            expected_status=http.HTTPStatus.CREATED,
        )
    )
    assert (instance := await repository.fetch_first(id=response_data.id))
    m2m_related_models = sorted(
        await instance.awaitable_attrs.m2m_related_models,
        key=lambda m2m_related_model: m2m_related_model.id,
    )
    assert len(m2m_related_models) == 2
    assert m2m_related_models[0].id == test_model.m2m_related_models_ids[0]
    assert m2m_related_models[1].id == test_model.m2m_related_models_ids[1]


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest_lazy_fixtures.lf("user_jwt_data"),
    ],
)
async def test_create_api_custom_detail_response(
    soft_delete_test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    soft_delete_repository: example_app.repositories.TestModelRepository,
    soft_delete_test_model: example_app.models.SoftDeleteTestModel,
) -> None:
    """Test create API with customized detail response."""
    schema = example_app.views.SoftDeleteTestModelAPIView.create_schema.model_validate(  # noqa: E501
        soft_delete_test_model,
    )
    schema.text_unique = "TextUnique"
    response = await api_client_factory(user).post(
        soft_delete_test_model_lazy_url(action_name="create"),
        json=schema.model_dump(mode="json"),
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return

    response_data = fastapi_rest_framework.testing.extract_schema_from_response(  # noqa: E501
        response=response,
        schema=example_app.views.SoftDeleteTestModelAPIView.create_detail_schema,
        expected_status=http.HTTPStatus.CREATED,
    )
    assert await soft_delete_repository.exists(id=response_data.id)
    assert response_data.created
    assert not hasattr(response_data, "modified")
