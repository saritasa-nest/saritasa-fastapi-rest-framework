import warnings

import pytest

import example_app
import fastapi_rest_framework

from . import factories, shortcuts


async def test_validation_empty_body(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test create when user sends empty body."""
    response = await api_client_factory(user_jwt_data).post(
        lazy_url(action_name="create"),
        json="{}",
    )

    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body",
    )
    assert response_data.detail == (
        "Input should be a valid dictionary or object to extract fields from"
    )


@pytest.mark.parametrize(
    ["field", "expected_error"],
    [
        [
            "text",
            "Input should be a valid string",
        ],
        [
            "text_enum",
            "Input should be 'value1', 'value2' or 'value3'",
        ],
        [
            "number",
            "Input should be a valid integer",
        ],
        [
            "small_number",
            "Input should be a valid integer",
        ],
        [
            "decimal_number",
            "Decimal input should be an integer, float, string or Decimal object",  # noqa: E501
        ],
        [
            "boolean",
            "Input should be a valid boolean",
        ],
        [
            "text_list",
            "Input should be a valid list",
        ],
        [
            "date_time",
            "Input should be a valid datetime",
        ],
        [
            "date",
            "Input should be a valid date",
        ],
        [
            "timedelta",
            "Input should be a valid timedelta",
        ],
        [
            "json_field",
            "Input should be a valid dictionary",
        ],
        [
            "related_model_id",
            "Input should be a valid integer",
        ],
    ],
)
async def test_create_api_invalid_types(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
    field: str,
    expected_error: str,
) -> None:
    """Test create when user send invalid types."""
    schema = example_app.views.TestModelAPIView.create_schema.model_validate(
        test_model,
    )
    setattr(schema, field, None)
    response = await api_client_factory(user_jwt_data).post(
        lazy_url(action_name="create"),
        json=schema.model_dump(mode="json"),
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field=f"body.{field}",
    )
    assert response_data.detail == expected_error, response_data


async def test_create_api_invalid_list_type_item(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test create when user send invalid item in list."""
    schema = example_app.views.TestModelAPIView.create_schema.model_validate(
        test_model,
    )
    schema.text_list = ["1", 2, "3"]
    # Ignore pydantic warning about int and str types
    with warnings.catch_warnings(action="ignore"):
        json_data = schema.model_dump(mode="json")
    response = await api_client_factory(user_jwt_data).post(
        lazy_url(action_name="create"),
        json=json_data,
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body.text_list.1",
    )
    assert (
        response_data.detail == "Input should be a valid string"
    ), response_data


async def test_create_api_failed_validation(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test create when user send invalid data."""
    schema = example_app.views.TestModelAPIView.create_schema.model_validate(
        test_model,
    )
    schema.related_model_id = -1
    schema.related_model_id_nullable = -1
    response = await api_client_factory(user_jwt_data).post(
        lazy_url(action_name="create"),
        json=schema.model_dump(mode="json"),
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body.related_model_id",
    )
    assert response_data.detail == "Related model was not found", response_data
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body.related_model_id_nullable",
    )
    assert response_data.detail == "Related model was not found", response_data


async def test_create_api_failed_validation_list(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test create when user send invalid data in list."""
    schema = example_app.views.TestModelAPIView.create_schema.model_validate(
        test_model,
    )
    schema.text_list = ["1", "invalid", "2"]
    schema.text_list_nullable = ["1", "2", "invalid"]
    response = await api_client_factory(user_jwt_data).post(
        lazy_url(action_name="create"),
        json=schema.model_dump(mode="json"),
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body.text_list.1",
    )
    assert response_data.detail == "Value is invalid", response_data
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body.text_list_nullable.2",
    )
    assert response_data.detail == "Value is invalid", response_data


async def test_create_api_unique_together(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test create API with unique together failure."""
    test_model.m2m_related_models_ids = []
    schema = example_app.views.TestModelAPIView.create_schema.model_validate(
        test_model,
    )
    schema.text_unique = "TextUnique"
    response = await api_client_factory(user_jwt_data).post(
        lazy_url(action_name="create"),
        json=schema.model_dump(mode="json"),
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body",
    )
    assert response_data.detail == (
        "Values of fields ('text', 'text_nullable') "
        "should be unique together."
    ), response_data


async def test_update_api_unique_together(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test update API with unique together failure."""
    test_model.m2m_related_models_ids = []
    new_test_model = await factories.TestModelFactory.create_async(
        repository.db_session,
    )
    schema = example_app.views.TestModelAPIView.create_schema.model_validate(
        test_model,
    )
    schema.text = new_test_model.text
    schema.text_nullable = new_test_model.text_nullable
    response = await api_client_factory(user_jwt_data).put(
        lazy_url(action_name="update", pk=test_model.id),
        json=schema.model_dump(mode="json"),
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body",
    )
    assert response_data.detail == (
        "Values of fields ('text', 'text_nullable') "
        "should be unique together."
    ), response_data


async def test_create_api_regex_validation(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test create when user fails regex validation."""
    test_model.m2m_related_models_ids = []
    schema = example_app.views.TestModelAPIView.create_schema.model_validate(
        test_model,
    )
    schema.text_nullable = "123456"
    response = await api_client_factory(user_jwt_data).post(
        lazy_url(action_name="create"),
        json=schema.model_dump(mode="json"),
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body.text_nullable",
    )
    assert response_data.detail == "Regex validation failed", response_data


async def test_create_api_unique_by_field_validation(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test create when user fails unique by field validation."""
    test_model.m2m_related_models_ids = []
    schema = example_app.views.TestModelAPIView.create_schema.model_validate(
        test_model,
    )
    response = await api_client_factory(user_jwt_data).post(
        lazy_url(action_name="create"),
        json=schema.model_dump(mode="json"),
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body.text_unique",
    )
    assert (
        response_data.detail
        == "There is already an instance with same Text unique"
    ), response_data


async def test_create_api_invalid_fk(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test create when user fails foreign key validation."""
    test_model.m2m_related_models_ids = []
    schema = example_app.views.TestModelAPIView.create_schema.model_validate(
        test_model,
    )
    schema.related_model_id = -1
    response = await api_client_factory(user_jwt_data).post(
        lazy_url(action_name="create"),
        json=schema.model_dump(mode="json"),
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body.related_model_id",
    )
    assert response_data.detail == "Related model was not found", response_data
