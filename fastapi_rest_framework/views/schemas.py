import typing

import pydantic


class BaseModel(pydantic.BaseModel):
    """Base model for schemas."""

    model_config = pydantic.ConfigDict(from_attributes=True)


PaginatedBaseModel = typing.TypeVar(
    "PaginatedBaseModel",
    bound=pydantic.BaseModel,
)


class PaginatedResult(BaseModel, typing.Generic[PaginatedBaseModel]):
    """Representation of paginated result."""

    count: int
    results: list[PaginatedBaseModel]
