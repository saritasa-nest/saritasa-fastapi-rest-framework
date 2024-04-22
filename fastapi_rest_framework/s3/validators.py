import collections.abc
import typing

import humanize

import fastapi_rest_framework

from . import context_mixins, schemas, utils


class S3URLValidator(
    context_mixins.S3ContextMixin,
    fastapi_rest_framework.BaseValidator[
        str | collections.abc.Sequence[str],
        str | collections.abc.Sequence[str],
    ],
):
    """Check that s3 url is valid one and extract it's key."""

    async def _validate(
        self,
        value: str | collections.abc.Sequence[str] | None,
        loc: fastapi_rest_framework.LOCType,
        context: fastapi_rest_framework.ContextType,
    ) -> str | collections.abc.Sequence[str] | None:
        if not value:
            return value  # pragma: no cover
        if isinstance(value, str):
            return await self._validate_str(
                value=value,
                loc=loc,
                context=context,
            )
        return await self._validate_sequence(
            value=value,
            loc=loc,
            context=context,
        )

    async def _validate_str(
        self,
        value: str,
        loc: fastapi_rest_framework.LOCType,
        context: fastapi_rest_framework.ContextType,
    ) -> str:
        s3_client = self.get_s3_client_from_context(context)
        key = utils.extract_key_from_url(
            value,
            bucket=s3_client.default_bucket,
        )
        if not key or not await s3_client.async_is_file_in_bucket(key=key):
            raise fastapi_rest_framework.ValidationError(
                error_type=fastapi_rest_framework.ValidationErrorType.not_found,
                error_message="File was not found",
            )
        return key

    async def _validate_sequence(
        self,
        value: collections.abc.Sequence[str],
        loc: fastapi_rest_framework.LOCType,
        context: fastapi_rest_framework.ContextType,
    ) -> collections.abc.Sequence[str]:
        s3_client = self.get_s3_client_from_context(context)
        keys = [
            utils.extract_key_from_url(
                url=url,
                bucket=s3_client.default_bucket,
            )
            for url in value
        ]
        errors = []
        for index, key in enumerate(keys):
            if not key or not await s3_client.async_is_file_in_bucket(key=key):
                errors.append(
                    fastapi_rest_framework.ValidationError(
                        error_type=fastapi_rest_framework.ValidationErrorType.not_found,
                        error_message="File was not found",
                        loc=(*loc, index),
                    ),
                )
        if errors:
            raise fastapi_rest_framework.ValidationError(
                all_errors=errors,
            )
        return keys


class S3RequestParamsValidator(
    fastapi_rest_framework.BaseValidator[
        schemas.S3RequestParams[typing.Any],
        schemas.S3RequestParams[typing.Any],
    ],
):
    """Validate request params for s3."""

    async def _validate(
        self,
        value: schemas.S3RequestParams[typing.Any] | None,
        loc: fastapi_rest_framework.LOCType,
        context: fastapi_rest_framework.ContextType,
    ) -> schemas.S3RequestParams[typing.Any] | None:
        if not value:
            return value  # pragma: no cover
        errors: list[fastapi_rest_framework.ValidationError] = []
        if (
            value.s3_config.allowed
            and value.content_type not in value.s3_config.allowed
        ):
            expected = ", ".join(value.s3_config.allowed)
            errors.append(
                fastapi_rest_framework.ValidationError(
                    error_type=fastapi_rest_framework.ValidationErrorType.invalid,
                    error_message=(
                        f"Invalid file type - `{value.content_type}` of"
                        f" `{value.filename}`. Expected: {expected}."
                    ),
                ),
            )
            errors[-1].loc = (*loc, "content_type")
        if value.s3_config.content_length_range:
            min_bound, max_bound = value.s3_config.content_length_range
            if min_bound > value.content_length:
                errors.append(
                    fastapi_rest_framework.ValidationError(
                        error_type=fastapi_rest_framework.ValidationErrorType.invalid,
                        error_message=(
                            "Invalid file size "
                            f"- {humanize.naturalsize(value.content_length)} "
                            f"of {value.filename}. "
                            f"Need between {humanize.naturalsize(min_bound)} "
                            f"and {humanize.naturalsize(max_bound)}."
                        ),
                    ),
                )
                errors[-1].loc = (*loc, "content_length")
            if max_bound < value.content_length:
                errors.append(
                    fastapi_rest_framework.ValidationError(
                        error_type=fastapi_rest_framework.ValidationErrorType.invalid,
                        error_message=(
                            "Invalid file size "
                            f"- {humanize.naturalsize(value.content_length)} "
                            f"of {value.filename}. "
                            f"Need between {humanize.naturalsize(min_bound)} "
                            f"and {humanize.naturalsize(max_bound)}."
                        ),
                    ),
                )
                errors[-1].loc = (*loc, "content_length")
        if errors:
            raise fastapi_rest_framework.ValidationError(all_errors=errors)
        return value
