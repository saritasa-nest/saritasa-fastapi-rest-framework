import abc
import enum
import typing

from . import schemas, types


class ValidationErrorType(enum.StrEnum):
    """Representation error types."""

    unique = "unique"
    invalid = "invalid"
    blank = "blank"
    not_found = "not_found"


class BaseValidator(
    typing.Generic[
        types.AnyGenericInput,
        types.AnyGenericOutput,
    ],
):
    """Base class for validations."""

    async def __call__(
        self,
        value: types.AnyGenericInput,
        context: dict[str, typing.Any],
        loc: types.LOCType = ("body",),
    ) -> types.AnyGenericOutput | None:
        """Validate data."""
        try:
            validated_value = await self._validate(
                value=value,
                context=context,
                loc=loc,
            )
        except ValidationError as validation_error:
            validation_error.loc = loc
            if validation_error.all_errors:
                raise validation_error from validation_error
            validation_error_list = ValidationError(
                all_errors=[validation_error],
            )
            validation_error_list.loc = validation_error.loc
            raise validation_error_list from validation_error
        return validated_value

    @abc.abstractmethod
    async def _validate(
        self,
        value: types.AnyGenericInput,
        loc: types.LOCType,
        context: dict[str, typing.Any],
    ) -> types.AnyGenericOutput | None:
        """Validate data and raise ValidationError on fail."""


class ValidationError(Exception):
    """Exception representing issue in input data."""

    def __init__(
        self,
        error_type: ValidationErrorType | None = None,
        error_message: str | None = None,
        all_errors: list[typing.Self] | None = None,
    ) -> None:
        self.error_type: ValidationErrorType | None = error_type
        self.error_message: str | None = error_message
        self.all_errors: list[typing.Self] | None = all_errors
        self.loc: types.LOCType
        if self.all_errors and self.error_message:
            raise ValueError("ValidationError can only have error or errors")
        if not self.all_errors and not self.error_message:
            raise ValueError("ValidationError has not errors")

    def get_schema(
        self,
    ) -> schemas.ValidationErrorSchema | list[schemas.ValidationErrorSchema]:
        """Transform validation error in schema."""
        if self.error_message and self.error_type:
            return schemas.ValidationErrorSchema(
                field=".".join(map(str, self.loc)),
                type=self.error_type,
                detail=self.error_message,
            )
        if self.all_errors:
            errors: list[schemas.ValidationErrorSchema] = []
            for error in map(self.__class__.get_schema, self.all_errors):
                if isinstance(error, list):
                    errors += error
                else:
                    errors.append(error)
            return errors
        raise ValueError("ValidationError has not errors")
