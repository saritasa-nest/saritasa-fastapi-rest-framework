import collections.abc
import typing

from .. import common_types, metrics, repositories
from . import core, types


class ObjectPKValidator(
    core.BaseValidator[
        int | collections.abc.Sequence[int],
        int | collections.abc.Sequence[int],
    ],
    typing.Generic[
        repositories.ApiRepositoryProtocolT,
        repositories.APIModelT,
    ],
):
    """Check that ids of object is present in database."""

    def __init__(
        self,
        repository: repositories.ApiRepositoryProtocolT,
        human_name: str,
        pk_attr: str = "id",
    ) -> None:
        super().__init__()
        self.repository = repository
        self.human_name = human_name
        self.pk_attr = pk_attr

    @metrics.tracker
    async def _validate(
        self,
        value: int | collections.abc.Sequence[int] | None,
        loc: types.LOCType,
        context: common_types.ContextType,
    ) -> int | collections.abc.Sequence[int] | None:
        if value is None:
            return value

        value_set = set(
            value if isinstance(value, collections.abc.Iterable) else [value],
        )
        objs_count = await self.repository.count(
            where=[
                getattr(self.repository.model, self.pk_attr).in_(value_set),
            ],
        )
        if objs_count < len(value_set):
            raise core.ValidationError(
                error_type=core.ValidationErrorType.not_found,
                error_message=f"{self.human_name.capitalize()} was not found",
            )
        if isinstance(value, collections.abc.Iterable):
            return list(value_set)
        return value_set.pop()


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

    @metrics.tracker
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
                getattr(
                    self.repository.model,
                    self.repository.model.pk_field,
                )
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
