import pydantic


class BaseModel(pydantic.BaseModel):
    """Base model for schemas."""

    model_config = pydantic.ConfigDict(
        from_attributes=True,
    )


class ValidationErrorSchema(BaseModel):
    """Representation of validation error."""

    field: str
    detail: str
    type: str


class GenericError(BaseModel):
    """Representation of generic error."""

    type: str
    detail: str
    errors: list[ValidationErrorSchema] = []
