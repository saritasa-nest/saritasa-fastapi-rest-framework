import collections.abc
import http
import json
import typing

import cryptography.hazmat.backends
import cryptography.hazmat.primitives.asymmetric.rsa
import cryptography.hazmat.primitives.serialization
import fastapi
import httpx
import pydantic
import starlette.datastructures

from . import validators, views

ResponseT = typing.TypeVar("ResponseT", bound=pydantic.BaseModel)

LazyUrl: typing.TypeAlias = collections.abc.Callable[
    ...,
    starlette.datastructures.URLPath,
]


def lazy_url(
    app: fastapi.FastAPI,
    view: type[
        views.BaseAPIView[
            typing.Any,
            typing.Any,
            typing.Any,
            typing.Any,
            typing.Any,
            typing.Any,
            typing.Any,
            typing.Any,
        ]
    ],
    action_name: str,
    **params: typing.Any,
) -> starlette.datastructures.URLPath:
    """Construct url for branch events."""
    return app.url_path_for(
        f"{view.get_basename()}-{action_name}",
        **params or {},
    )


def extract_json_from_response(
    response: httpx.Response,
) -> dict[str, typing.Any] | list[dict[str, typing.Any]]:
    """Extract json from response."""
    try:
        return response.json()
    except json.decoder.JSONDecodeError:
        return {}


def extract_schema_from_response(
    response: httpx.Response,
    schema: type[ResponseT],
    expected_status: http.HTTPStatus = http.HTTPStatus.OK,
) -> ResponseT:
    """Extract schema from response."""
    data = extract_json_from_response(response=response)
    assert response.status_code == expected_status, data
    assert isinstance(data, dict), data
    return schema.model_validate(data)


def extract_paginated_result_from_response(
    response: httpx.Response,
    schema: type[ResponseT],
    expected_status: http.HTTPStatus = http.HTTPStatus.OK,
) -> views.PaginatedResult[ResponseT]:
    """Extract paginated result from response."""
    return extract_schema_from_response(
        response=response,
        schema=views.PaginatedResult[schema],
        expected_status=expected_status,
    )


def extract_schema_list_from_response(
    response: httpx.Response,
    schema: type[ResponseT],
    expected_status: http.HTTPStatus = http.HTTPStatus.OK,
) -> list[ResponseT]:
    """Extract schema list from response."""
    data = extract_json_from_response(response=response)
    assert response.status_code == expected_status, data
    assert isinstance(data, list), data
    return list(map(schema.model_validate, data))


def extract_general_errors_from_response(
    response: httpx.Response,
    expected_status: http.HTTPStatus = http.HTTPStatus.UNPROCESSABLE_ENTITY,
) -> validators.GenericError:
    """Extract response error."""
    return extract_schema_from_response(
        response=response,
        expected_status=expected_status,
        schema=validators.GenericError,
    )


def extract_error_from_response(
    response: httpx.Response,
    field: str,
    expected_status: http.HTTPStatus = http.HTTPStatus.UNPROCESSABLE_ENTITY,
) -> validators.ValidationErrorSchema:
    """Extract response error."""
    data = extract_general_errors_from_response(response, expected_status)
    assert (
        expected_error := next(
            (error for error in data.errors if error.field == field),
            None,
        )
    ), data
    return expected_error


def has_auth_header(
    api_client: httpx.AsyncClient,
    auth_header: str = "Authorization",
) -> bool:
    """Check it api client has auth token."""
    return auth_header in api_client.headers


def validate_auth_required_response(
    response: httpx.Response,
    auth_header: str = "Authorization",
    expected_status: http.HTTPStatus = http.HTTPStatus.UNAUTHORIZED,
) -> bool:
    """Check that response contains requirement for token."""
    if auth_header in response.request.headers:
        return True

    data = extract_json_from_response(response=response)
    assert response.status_code == expected_status, data
    return False


def validate_response_status(
    response: httpx.Response,
    expected_status: http.HTTPStatus = http.HTTPStatus.OK,
) -> None:
    """Check that response is not found."""
    data = extract_json_from_response(response=response)
    assert response.status_code == expected_status, data


def validate_not_found(
    response: httpx.Response,
) -> None:
    """Check that response is not found."""
    validate_response_status(
        response=response,
        expected_status=http.HTTPStatus.NOT_FOUND,
    )


def validate_no_content(
    response: httpx.Response,
) -> None:
    """Check that response is no content."""
    validate_response_status(
        response=response,
        expected_status=http.HTTPStatus.NO_CONTENT,
    )


def generate_private_and_public_key_for_rs256_jwt() -> tuple[str, str]:
    """Generate private key and public key for jwt generation."""
    private_key = (
        cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=cryptography.hazmat.backends.default_backend(),
        )
    )
    public_key = private_key.public_key()
    return (
        private_key.private_bytes(
            cryptography.hazmat.primitives.serialization.Encoding.PEM,
            cryptography.hazmat.primitives.serialization.PrivateFormat.PKCS8,
            cryptography.hazmat.primitives.serialization.NoEncryption(),
        ).decode("utf-8"),
        public_key.public_bytes(
            encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM,
            format=cryptography.hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8"),
    )
