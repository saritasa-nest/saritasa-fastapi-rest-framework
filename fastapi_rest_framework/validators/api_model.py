import abc
import collections.abc
import dataclasses
import enum
import operator
import typing

from .. import common_types, metrics, repositories
from . import core, types

UniqueConstraintType: typing.TypeAlias = tuple[str, ...]
ValidationMapType: typing.TypeAlias = dict[
    str,
    tuple["core.BaseValidator[typing.Any, typing.Any]", ...],
]


class ComparisonOperatorEnum(enum.Enum):
    """Enum for possible operators."""

    EQ = "=="
    NE = "!="
    GT = ">"
    LT = "<"
    GE = ">="
    LE = "<="


AVAILABLE_OPERATORS: dict[ComparisonOperatorEnum, typing.Any] = {
    ComparisonOperatorEnum.EQ: operator.eq,
    ComparisonOperatorEnum.NE: operator.ne,
    ComparisonOperatorEnum.GT: operator.gt,
    ComparisonOperatorEnum.LT: operator.lt,
    ComparisonOperatorEnum.GE: operator.ge,
    ComparisonOperatorEnum.LE: operator.le,
}


@dataclasses.dataclass(frozen=True)
class UniqueCondition:
    """Representation of condition for unique constraints."""

    field_name: str
    value: typing.Any
    operator: ComparisonOperatorEnum


class BaseModelValidator(
    core.BaseValidator[types.ApiDataType, types.ApiDataType],
    typing.Generic[
        repositories.ApiRepositoryProtocolT,
        repositories.APIModelT,
    ],
):
    """Base validator for models."""

    def __init__(
        self,
        repository: repositories.ApiRepositoryProtocolT,
        instance: repositories.APIModelT | None = None,
        pk_field: str = "id",
    ) -> None:
        self.instance = instance
        self.repository = repository
        self.pk_field: str = pk_field

    def _get_validation_map(
        self,
        value: types.ApiDataType,
        context: common_types.ContextType,
    ) -> ValidationMapType:
        """Get validation map/plan for model."""
        return {}

    def _get_extra_unique_conditions(self) -> list[UniqueCondition]:
        """Additional condition for checking unique constraints."""
        return []

    def _get_unique_constraints(self) -> list[UniqueConstraintType]:
        """Get unique constraints for model."""
        return []

    @metrics.tracker
    async def _validate_unique_constraints(
        self,
        data: types.ApiDataType,
        unique_constraints: collections.abc.Sequence[UniqueConstraintType],
        extra_unique_conditions: collections.abc.Sequence[UniqueCondition],
    ) -> types.ApiDataType:
        """Validate unique constraints for model.

        Check if entry with unique constraint fields exists in DB. Also, you
        can pass extra conditions for checking. For example: you create unique
        constraint for fields `name` and `is_active` with condition
        `is_active` == True. So you can create objects of `UniqueCondition`
        class in `_get_extra_unique_conditions` method and return them:

        ```
            UniqueCondition(
                field_name="is_active",
                operator=ComparisonOperatorEnum.EQ,
                value=True,
            )
        ```

        """
        extra_where_conditions = [
            AVAILABLE_OPERATORS[condition.operator](
                getattr(self.repository.model, condition.field_name),
                condition.value,
            )
            for condition in extra_unique_conditions
        ]

        for constraint in unique_constraints:
            if await self.repository.exists(
                where=[
                    getattr(self.repository.model, self.pk_field)
                    != getattr(self.instance, self.pk_field, None),
                    *extra_where_conditions,
                ],
                **{field_name: data[field_name] for field_name in constraint},
            ):
                raise core.ValidationError(
                    error_message=(
                        f"Values of fields {constraint} should be unique "
                        "together."
                    ),
                    error_type=core.ValidationErrorType.unique,
                )
        return data

    @metrics.tracker
    async def _validate(
        self,
        value: types.ApiDataType,
        loc: types.LOCType,
        context: common_types.ContextType,
    ) -> types.ApiDataType:
        """Perform data validation.

        It's done in two steps, first we prepare validation map, then we
        use it validate_data to perform validation.

        """
        value = await self._validate_data(
            data=value,
            validation_map=self._get_validation_map(
                value=value,
                context=context,
            ),
            loc=loc,
            context=context,
        )
        value = await self._validate_unique_constraints(
            data=value,
            unique_constraints=self._get_unique_constraints(),
            extra_unique_conditions=self._get_extra_unique_conditions(),
        )
        return await self.validate_body(
            value=value,
            context=context,
        )

    @metrics.tracker
    async def validate_body(
        self,
        value: types.ApiDataType,
        context: common_types.ContextType,
    ) -> types.ApiDataType:
        """Perform validation against whole input data(body)."""
        return value

    @metrics.tracker
    async def _validate_data(
        self,
        data: types.ApiDataType,
        validation_map: ValidationMapType,
        loc: types.LOCType,
        context: common_types.ContextType,
    ) -> types.ApiDataType:
        """Validate data according to validation_map."""
        errors: list[core.ValidationError] = []
        for field, value in data.items():
            if field not in validation_map:
                continue
            for validator in validation_map[field]:
                try:
                    value = await validator(
                        value=value,
                        loc=(*loc, field),
                        context=context,
                    )
                except core.ValidationError as validation_error:
                    if validation_error.all_errors:
                        errors += validation_error.all_errors
                    else:
                        errors.append(validation_error)
            data[field] = value
        if errors:
            raise core.ValidationError(all_errors=errors)
        return data


class BaseModelListValidator(
    core.BaseValidator[
        collections.abc.Sequence[types.ApiDataType],
        collections.abc.Sequence[types.ApiDataType],
    ],
    typing.Generic[
        repositories.ApiRepositoryProtocolT,
        repositories.APIModelT,
    ],
):
    """Base list model validator based on single instance model validator."""

    def __init__(
        self,
        instance_validator: type[
            BaseModelValidator[
                repositories.ApiRepositoryProtocolT,
                repositories.APIModelT,
            ],
        ],
        repository: repositories.ApiRepositoryProtocolT,
    ) -> None:
        self.repository = repository
        self.instance_validator = instance_validator

    @abc.abstractmethod
    @metrics.tracker
    async def _validate(
        self,
        value: collections.abc.Sequence[types.ApiDataType],
        loc: types.LOCType,
        context: common_types.ContextType,
    ) -> collections.abc.Sequence[types.ApiDataType]:
        """Validate sequence of api data."""
        validated_data: list[types.ApiDataType] = []
        errors: list[core.ValidationError] = []
        for index, data in enumerate(value):
            try:
                validated_value = await self.instance_validator(
                    repository=self.repository,
                )(
                    value=data,
                    loc=(*loc, index),
                    context=context,
                )
                if validated_value:
                    validated_data.append(validated_value)
            except core.ValidationError as validation_error:
                if validation_error.all_errors:
                    errors += validation_error.all_errors
                else:
                    errors.append(validation_error)
        if errors:
            raise core.ValidationError(all_errors=errors)
        return validated_data
