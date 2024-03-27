import warnings

import pytest

import example_app
import fastapi_rest_framework

from . import shortcuts


async def test_validation_empty_body(
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model: example_app.models.TestModel,
) -> None:
    """Test create when user sends empty body."""
    response = await auth_api_client_factory(user_jwt_data).post(
        test_model_lazy_url(action_name="create"),
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
            "Input should be a valid string",
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
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
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
    response = await auth_api_client_factory(user_jwt_data).post(
        test_model_lazy_url(action_name="create"),
        json=schema.model_dump(mode="json"),
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field=f"body.{field}",
    )
    assert response_data.detail == expected_error, response_data


async def test_create_api_invalid_list_type_item(
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
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
    response = await auth_api_client_factory(user_jwt_data).post(
        test_model_lazy_url(action_name="create"),
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
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
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
    response = await auth_api_client_factory(user_jwt_data).post(
        test_model_lazy_url(action_name="create"),
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
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
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
    response = await auth_api_client_factory(user_jwt_data).post(
        test_model_lazy_url(action_name="create"),
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
