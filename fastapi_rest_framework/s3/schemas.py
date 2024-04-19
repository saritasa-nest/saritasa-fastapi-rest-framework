import collections.abc
import enum
import typing

import pydantic
import saritasa_s3_tools

S3ConfigT = typing.TypeVar("S3ConfigT", bound=enum.StrEnum)


class S3RequestParams(pydantic.BaseModel, typing.Generic[S3ConfigT]):
    """Request for getting params for s3 upload."""

    config: S3ConfigT
    filename: str
    content_type: str
    content_length: int

    @property
    def s3_config(self) -> saritasa_s3_tools.S3FileTypeConfig:
        """Get s3 config."""
        return saritasa_s3_tools.S3FileTypeConfig.configs[self.config]


S3Params = pydantic.create_model(
    "S3Params",
    __base__=pydantic.BaseModel,
    success_action_status=(int | None, None),
    **{  # type: ignore
        field: (str | None, None)
        for field in (
            "Content-Disposition",
            "x-amz-meta-user-id",
            "x-amz-meta-config-name",
            "Content-Type",
            "key",
            "AWSAccessKeyId",
            "x-amz-security-token",
            "x-amz-algorithm",
            "x-amz-credential",
            "x-amz-date",
            "policy",
            "signature",
            "x-amz-signature",
        )
    },
)


class S3UploadParams(pydantic.BaseModel):
    """Upload params to s3."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    url: pydantic.AnyHttpUrl
    params: S3Params  # type: ignore


def add_auth_params_to_urls(
    cls: pydantic.BaseModel,
    value: str | collections.abc.Sequence[str],
    info: pydantic.ValidationInfo,
) -> str | collections.abc.Sequence[str]:
    """Generate presigned_url for s3 file."""
    if not value:
        return value  # pragma: no cover
    if info.context and "s3_client" in info.context:
        if isinstance(value, str):
            return info.context["s3_client"].generate_presigned_url(
                key=value,
            )
        else:
            return list(
                map(
                    info.context["s3_client"].generate_presigned_url,
                    value,
                ),
            )
    return value
