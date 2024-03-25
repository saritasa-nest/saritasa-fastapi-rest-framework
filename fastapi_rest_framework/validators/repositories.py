import typing

from .. import common_types, repositories
from . import core, types


class ObjectPKValidator(
    core.BaseValidator[int, int],
    typing.Generic[
        repositories.ApiRepositoryProtocolT,
        repositories.APIModelT,
    ],
):
    """Check that id of object is present in database."""

    def __init__(
        self,
        repository: repositories.ApiRepositoryProtocolT,
        human_name: str,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.human_name: str = human_name
        self.instance: repositories.APIModelT

    async def _validate(
        self,
        value: int | None,
        loc: types.LOCType,
        context: common_types.ContextType,
    ) -> int | None:
        if value is None:
            return value
        obj = await self.repository.fetch_first(id=value)
        if not obj:
            raise core.ValidationError(
                error_type=core.ValidationErrorType.not_found,
                error_message=f"{self.human_name.capitalize()} was not found",
            )
        self.instance = obj
        return value


class UniqueByFieldValidator(
    core.BaseValidator[
        types.AnyGenericInput,
        types.AnyGenericOutput,
    ],
    typing.Generic[
        types.AnyGenericInput,
        types.AnyGenericOutput,
        repositories.ApiRepositoryProtocolT,
        repositories.APIModelT,
    ],
):
    """Check data is unique against a field."""

    def __init__(
        self,
        field: str,
        repository: repositories.ApiRepositoryProtocolT,
        human_name: str,
        instance: repositories.APIModelT | None,
    ) -> None:
        super().__init__()
        self.field = field
        self.repository = repository
        self.human_name = human_name
        self.instance = instance

    async def _validate(
        self,
        value: types.AnyGenericInput | None,
        loc: types.LOCType,
        context: common_types.ContextType,
    ) -> types.AnyGenericOutput | None:
        if value is None:
            return value
        found_count = await self.repository.count(
            where=[
                self.repository.model.pk_field
                != getattr(
                    self.instance,
                    self.repository.model.pk_field,
                    None,
                ),
            ],
            **{self.field: value},
        )
        if found_count:
            raise core.ValidationError(
                error_type=core.ValidationErrorType.unique,
                error_message=(
                    f"There is already an instance with same {self.human_name}"
                ),
            )
        return value
