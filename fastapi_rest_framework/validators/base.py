import collections.abc
import datetime
import re
import typing
import zoneinfo

from .. import metrics
from . import core, types


class DatetimeValidator(
    core.BaseValidator[
        datetime.datetime,
        datetime.datetime,
    ],
):
    """Validate datetime."""

    @metrics.tracker
    async def _validate(
        self,
        value: datetime.datetime | None,
        loc: types.LOCType,
        context: dict[str, typing.Any],
    ) -> datetime.datetime | None:
        """Strip timezone info sqlalchemy doesn't do it for us."""
        if not value:
            return value
        return value.replace(tzinfo=None)


class RegexValidator(core.BaseValidator[str, str]):
    """Validate string against regex."""

    def __init__(
        self,
        pattern: str,
        human_error: str,
    ) -> None:
        super().__init__()
        self.pattern: str = pattern
        self.human_error: str = human_error

    @metrics.tracker
    async def _validate(
        self,
        value: str | None,
        loc: types.LOCType,
        context: dict[str, typing.Any],
    ) -> str | None:
        if not value:
            return value
        if not re.match(pattern=self.pattern, string=value):
            raise core.ValidationError(
                error_type=core.ValidationErrorType.invalid,
                error_message=self.human_error,
            )
        return value


class TimeZoneValidator(core.BaseValidator[str, str]):
    """Validate timezone."""

    @metrics.tracker
    async def _validate(
        self,
        value: str | None,
        loc: types.LOCType,
        context: dict[str, typing.Any],
    ) -> str | None:
        if value is None:
            return value
        try:
            zoneinfo.ZoneInfo(key=value)
        except (ValueError, zoneinfo.ZoneInfoNotFoundError) as error:
            raise core.ValidationError(
                error_type=core.ValidationErrorType.not_found,
                error_message="Invalid timezone or timezone not supported",
            ) from error
        return value


class NotEqualToValues(
    core.BaseValidator[
        types.AnyGenericInput,
        types.AnyGenericOutput,
    ],
    typing.Generic[
        types.AnyGenericInput,
        types.AnyGenericOutput,
    ],
):
    """Check that input value is not equal to values."""

    def __init__(
        self,
        values: collections.abc.Sequence[types.AnyGenericInput | None],
        human_msg: str | None = None,
    ) -> None:
        super().__init__()
        self.values = values
        self.human_msg: str | None = human_msg

    @metrics.tracker
    async def _validate(
        self,
        value: types.AnyGenericInput | None,
        loc: types.LOCType,
        context: dict[str, typing.Any],
    ) -> types.AnyGenericOutput | None:
        if value is None:
            return value
        if value in self.values:
            values_str = ",".join(map(str, self.values))
            default_msg = f"Input value can't be one this: {values_str}"
            raise core.ValidationError(
                error_type=core.ValidationErrorType.unique,
                error_message=self.human_msg or default_msg,
            )
        return value
