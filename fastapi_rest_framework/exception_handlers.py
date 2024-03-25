import http

import fastapi

from . import validators


def _get_http_type(exc: fastapi.HTTPException) -> str:
    """Get type of error depending on status."""
    match exc.status_code:
        case http.HTTPStatus.NOT_FOUND:
            return "not_found"
        case http.HTTPStatus.UNAUTHORIZED:
            return "authorization"
        case http.HTTPStatus.FORBIDDEN:
            return "permission"
    return "error"


async def http_exception_handler(
    request: fastapi.Request,
    exc: fastapi.HTTPException,
) -> fastapi.responses.JSONResponse:
    """Handle fastapi.HTTPException errors."""
    return fastapi.responses.JSONResponse(
        content=validators.GenericError(
            type=_get_http_type(exc),
            detail=exc.detail,
        ).model_dump(mode="json"),
        status_code=exc.status_code,
    )


async def pydantic_validation_error_exception_handler(
    request: fastapi.Request,
    exc: fastapi.exceptions.RequestValidationError,
) -> fastapi.responses.JSONResponse:
    """Handle pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append(
            validators.ValidationErrorSchema(
                type=error["type"],
                field=".".join(map(str, error["loc"])),
                detail=error["msg"],
            ),
        )
    return fastapi.responses.JSONResponse(
        content=validators.GenericError(
            type="validation",
            errors=errors,
            detail="There are validation errors in your request",
        ).model_dump(mode="json"),
        status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY,
    )


async def validation_error_exception_handler(
    request: fastapi.Request,
    exc: validators.ValidationError,
) -> fastapi.responses.JSONResponse:
    """Handle validation errors."""
    error_schema = exc.get_schema()
    if not isinstance(error_schema, list):
        raise TypeError("Expected list of errors, got singular")

    return fastapi.responses.JSONResponse(
        content=validators.GenericError(
            type="validation",
            errors=error_schema,
            detail="There are validation errors in your request",
        ).model_dump(mode="json"),
        status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY,
    )
