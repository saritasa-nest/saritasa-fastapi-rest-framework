import http

import humanize
import pytest
import saritasa_s3_tools

import example_app
import fastapi_rest_framework

from . import shortcuts


def get_s3_params_url() -> str:
    """Get s3 url."""
    return "/s3/"


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest.lazy_fixtures("user_jwt_data"),
    ],
)
async def test_auth_validation(
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData,
) -> None:
    """Test that anon user won't be able to get params."""
    response = await auth_api_client_factory(user).post(
        get_s3_params_url(),
        json=example_app.views.S3GetParamsView()
        .generate_request_params_schema()(
            config="files",
            filename="test.txt",
            content_type="text/plain",
            content_length=5000,
        )
        .model_dump(mode="json"),
    )
    if user is None:
        response_data = fastapi_rest_framework.testing.extract_general_errors_from_response(  # noqa
            response=response,
            expected_status=http.HTTPStatus.FORBIDDEN,
        )
        assert (
            response_data.detail == "User can't use this config for upload"
        ), response_data
        return
    fastapi_rest_framework.testing.extract_schema_from_response(
        response=response,
        schema=fastapi_rest_framework.s3.S3UploadParams,
    )


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest.lazy_fixtures("user_jwt_data"),
    ],
)
async def test_anon_auth_validation(
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData,
) -> None:
    """Test that if no auth config was set, anyone could upload file."""
    response = await auth_api_client_factory(user).post(
        get_s3_params_url(),
        json=example_app.views.S3GetParamsView()
        .generate_request_params_schema()(
            config="anon_files",
            filename="test.txt",
            content_type="text/plain",
            content_length=5000,
        )
        .model_dump(mode="json"),
    )
    fastapi_rest_framework.testing.extract_schema_from_response(
        response=response,
        schema=fastapi_rest_framework.s3.S3UploadParams,
    )


@pytest.mark.parametrize(
    argnames="content_length",
    argvalues=[
        4000,
        30000000,
    ],
)
async def test_content_length_validation(
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    content_length: int,
) -> None:
    """Test that user need set correct content_length."""
    response = await auth_api_client_factory(user_jwt_data).post(
        get_s3_params_url(),
        json=example_app.views.S3GetParamsView()
        .generate_request_params_schema()(
            config="files",
            filename="test.txt",
            content_type="text/plain",
            content_length=content_length,
        )
        .model_dump(mode="json"),
    )
    error = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body.content_length",
    )
    assert error.detail == (
        f"Invalid file size - {humanize.naturalsize(content_length)} of "
        "test.txt. Need between 5.0 kB and 20.0 MB."
    ), error


async def test_content_type_validation(
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
) -> None:
    """Test that user need set correct content_type."""
    response = await auth_api_client_factory(user_jwt_data).post(
        get_s3_params_url(),
        json=example_app.views.S3GetParamsView()
        .generate_request_params_schema()(
            config="files",
            filename="test.txt",
            content_type="test/pytest",
            content_length=5000,
        )
        .model_dump(mode="json"),
    )
    error = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="body.content_type",
    )
    assert error.detail == (
        "Invalid file type - `test/pytest` of `test.txt`. "
        "Expected: text/plain."
    ), error


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest.lazy_fixtures("user_jwt_data"),
    ],
)
async def test_all_files_allowed_validation(
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData,
) -> None:
    """Test that all files can be allowed."""
    response = await auth_api_client_factory(user).post(
        get_s3_params_url(),
        json=example_app.views.S3GetParamsView()
        .generate_request_params_schema()(
            config="all_file_types",
            filename="test.txt",
            content_type="test/test",
            content_length=5000,
        )
        .model_dump(mode="json"),
    )
    fastapi_rest_framework.testing.extract_schema_from_response(
        response=response,
        schema=fastapi_rest_framework.s3.S3UploadParams,
    )


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest.lazy_fixtures("user_jwt_data"),
    ],
)
async def test_all_file_sizes_allowed_validation(
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData,
) -> None:
    """Test that all files can be allowed."""
    response = await auth_api_client_factory(user).post(
        get_s3_params_url(),
        json=example_app.views.S3GetParamsView()
        .generate_request_params_schema()(
            config="all_file_sizes",
            filename="test.txt",
            content_type="text/plain",
            content_length=5000 * 10**10,
        )
        .model_dump(mode="json"),
    )
    fastapi_rest_framework.testing.extract_schema_from_response(
        response=response,
        schema=fastapi_rest_framework.s3.S3UploadParams,
    )


async def test_create_instance_with_file(
    test_model: example_app.models.TestModel,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    user_jwt_data: shortcuts.UserData,
    async_s3_client: saritasa_s3_tools.AsyncS3Client,
) -> None:
    """Test model creation with file upload."""
    schema = example_app.views.TestModelAPIView.create_schema.model_validate(
        test_model,
    )
    schema.text_unique = "TextUnique"
    schema.text_nullable = "TestValue"
    (
        schema.file,
        file_key,
    ) = await fastapi_rest_framework.s3.testing.upload_file_to_s3(
        api_client=auth_api_client_factory(user_jwt_data),
        config="all_file_types",
        file_path=__file__,
    )
    schema.files = [schema.file, schema.file]
    assert await fastapi_rest_framework.s3.testing.check_s3_key_is_valid(
        async_s3_client,
        file_key,
    )
    response = await auth_api_client_factory(user_jwt_data).post(
        test_model_lazy_url(action_name="create"),
        json=schema.model_dump(mode="json"),
    )
    response_data = (
        fastapi_rest_framework.testing.extract_schema_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.detail_schema,
            expected_status=http.HTTPStatus.CREATED,
        )
    )
    await fastapi_rest_framework.s3.testing.check_s3_url_is_valid(
        response_data.file,
    )
    file_metadata = (
        await async_s3_client.async_get_file_metadata(key=file_key)
    )["Metadata"]
    assert "user-id" in file_metadata, file_metadata
    assert file_metadata["user-id"] == str(user_jwt_data.id), file_metadata


async def test_update_instance_with_file(
    test_model: example_app.models.TestModel,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    user_jwt_data: shortcuts.UserData,
    async_s3_client: saritasa_s3_tools.AsyncS3Client,
) -> None:
    """Test model update with file upload."""
    schema = example_app.views.TestModelAPIView.update_schema.model_validate(
        test_model,
    )
    schema.text_unique = "TextUnique"
    schema.text_nullable = "TestValue"
    (
        schema.file,
        file_key,
    ) = await fastapi_rest_framework.s3.testing.upload_file_to_s3(
        api_client=auth_api_client_factory(user_jwt_data),
        config="all_file_types",
        file_path=__file__,
    )
    schema.files = [schema.file, schema.file]
    assert await fastapi_rest_framework.s3.testing.check_s3_key_is_valid(
        async_s3_client,
        file_key,
    )
    response = await auth_api_client_factory(user_jwt_data).put(
        test_model_lazy_url(
            action_name="update",
            pk=test_model.pk,
        ),
        json=schema.model_dump(mode="json"),
    )
    response_data = (
        fastapi_rest_framework.testing.extract_schema_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.detail_schema,
        )
    )
    await fastapi_rest_framework.s3.testing.check_s3_url_is_valid(
        response_data.file,
    )
    file_metadata = (
        await async_s3_client.async_get_file_metadata(key=file_key)
    )["Metadata"]
    assert "user-id" in file_metadata, file_metadata
    assert file_metadata["user-id"] == str(user_jwt_data.id), file_metadata


async def test_update_instance_with_non_existent_file(
    test_model: example_app.models.TestModel,
    auth_api_client_factory: shortcuts.AuthApiClientFactory,
    test_model_lazy_url: fastapi_rest_framework.testing.LazyUrl,
    user_jwt_data: shortcuts.UserData,
    async_s3_client: saritasa_s3_tools.AsyncS3Client,
) -> None:
    """Test model update with file that is not in bucket."""
    schema = example_app.views.TestModelAPIView.update_schema.model_validate(
        test_model,
    )
    schema.text_unique = "TextUnique"
    schema.text_nullable = "TestValue"
    schema.file = "https://www.google.com"
    schema.files = [schema.file, schema.file]
    response = await auth_api_client_factory(user_jwt_data).put(
        test_model_lazy_url(
            action_name="update",
            pk=test_model.pk,
        ),
        json=schema.model_dump(mode="json"),
    )
    for field in (
        "body.file",
        "body.files.0",
        "body.files.1",
    ):
        response_data = (
            fastapi_rest_framework.testing.extract_error_from_response(
                response=response,
                field=field,
            )
        )
        assert response_data.detail == "File was not found", response_data
