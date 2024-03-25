import http

from .. import validators
from . import types

DEFAULT_ERROR_RESPONSES: types.ResponsesMap = {
    http.HTTPStatus.UNAUTHORIZED: {
        "model": validators.GenericError,
        "content": {
            "application/json": {
                "example": [
                    validators.GenericError(
                        type="authorization",
                        detail="User authorization required.",
                    ).model_dump(),
                ],
            },
        },
    },
    http.HTTPStatus.FORBIDDEN: {
        "model": validators.GenericError,
        "content": {
            "application/json": {
                "example": [
                    validators.GenericError(
                        type="permission",
                        detail=(
                            "User doesn't have permission for this action."
                        ),
                    ).model_dump(),
                ],
            },
        },
    },
    http.HTTPStatus.NOT_FOUND: {
        "model": validators.GenericError,
        "content": {
            "application/json": {
                "example": [
                    validators.GenericError(
                        type="not_found",
                        detail="Not found.",
                    ).model_dump(),
                ],
            },
        },
    },
    http.HTTPStatus.UNPROCESSABLE_ENTITY: {
        "model": validators.GenericError,
        "content": {
            "application/json": {
                "example": [
                    validators.GenericError(
                        type="validation",
                        detail=(
                            "There are validation errors in your request."
                        ),
                        errors=[
                            validators.ValidationErrorSchema(
                                field="body.name",
                                detail="This field is required.",
                                type=validators.ValidationErrorType.invalid,
                            ),
                            validators.ValidationErrorSchema(
                                field="body.list.2.email",
                                detail="Enter a valid email address.",
                                type=validators.ValidationErrorType.invalid,
                            ),
                        ],
                    ).model_dump(),
                ],
            },
        },
    },
}
