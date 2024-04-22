import collections.abc
import enum
import typing

import fastapi
import pydantic
import pydantic.json_schema
import pydantic_core
import saritasa_s3_tools

from .. import metrics, views
from .. import permissions as core_permissions
from . import permissions, schemas, validators

S3ClientT = typing.TypeVar(
    "S3ClientT",
    bound=saritasa_s3_tools.AsyncS3Client,
)


class S3Config(enum.StrEnum):
    """Base class for S3Config enum."""

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: pydantic_core.core_schema.CoreSchema,
        handler: pydantic.GetJsonSchemaHandler,
    ) -> pydantic.json_schema.JsonSchemaValue:  # pragma: no cover
        """Adjust enum for openapi schema.

        Add names x-enum-varnames for better support of codegen.

        """
        generated_schema = handler(core_schema)
        generated_schema = handler.resolve_ref_schema(generated_schema)
        generated_schema["x-enum-varnames"] = [
            choice.name
            for choice in cls  # type: ignore
        ]
        return generated_schema


class S3GetParamsViewMeta(type):
    """Metaclass for BaseAPIView."""

    def __new__(
        cls,
        name,  # noqa: ANN001
        bases,  # noqa: ANN001
        attrs,  # noqa: ANN001
        **kwargs,
    ) -> type["S3GetParamsView[typing.Any, typing.Any]"]:
        """Register endpoint in router."""
        obj_cls: type[S3GetParamsView[typing.Any, typing.Any]] = (
            super().__new__(
                cls,  # type: ignore
                name,  # type: ignore
                bases,
                attrs,
                **kwargs,
            )
        )
        if not hasattr(obj_cls, "router"):
            return obj_cls
        obj_cls.register_endpoint()
        return obj_cls


class S3GetParamsView(
    typing.Generic[
        core_permissions.UserT,
        S3ClientT,
    ],
    metaclass=S3GetParamsViewMeta,
):
    """View for generating upload params for s3."""

    router: fastapi.APIRouter
    upload_folder: str = ""
    responses: views.ResponsesMap = views.DEFAULT_ERROR_RESPONSES
    user_dependency: type[core_permissions.UserT]
    s3_client_dependency: type[S3ClientT]

    @classmethod
    def register_endpoint(cls) -> None:
        """Register endpoint."""
        endpoint = cls()
        cls.router.post(
            "/",
            name="s3-params",
            responses=cls.responses,
        )(endpoint.get_endpoint())

    def generate_s3_config_enum(self) -> type[S3Config]:
        """Generate s3 configs enum."""
        return S3Config(  # type: ignore
            "S3Config",
            [
                (config, config)
                for config in saritasa_s3_tools.S3FileTypeConfig.configs
            ],
        )

    def generate_request_params_schema(
        self,
    ) -> type[schemas.S3RequestParams[typing.Any]]:
        """Generate request params schema."""

        class S3RequestParams(
            schemas.S3RequestParams[self.generate_s3_config_enum()],  # type: ignore
        ):
            """Params for s3 upload."""

        return S3RequestParams

    def get_endpoint(
        self,
    ) -> collections.abc.Callable[
        ...,
        collections.abc.Coroutine[
            typing.Any,
            typing.Any,
            schemas.S3UploadParams,
        ],
    ]:
        """Prepare endpoint."""

        async def _endpoint(
            user_data: self.user_dependency,  # type: ignore
            s3_request_params: self.generate_request_params_schema(),  # type: ignore
            s3_client: self.s3_client_dependency,  # type: ignore
        ) -> schemas.S3UploadParams:
            return await self.get_s3_params(
                user_data=user_data,
                s3_request_params=s3_request_params,
                s3_client=s3_client,
            )

        _endpoint.__doc__ = self.get_s3_params.__doc__
        return _endpoint

    @metrics.tracker
    async def get_s3_params(
        self,
        user_data: core_permissions.UserT,
        s3_request_params: schemas.S3RequestParams[typing.Any],
        s3_client: S3ClientT,
    ) -> schemas.S3UploadParams:
        """Get parameters for upload to S3 bucket.

        Current endpoint returns all required for direct s3 upload data, which
        should be later sent to `url` as form-data url with 'file'.

        Workflow:

        * First, you make request to this endpoint.
        * Then send response data to `url` via POST.

        """
        await permissions.S3ConfigPermission()(
            user=user_data,
            action="",
            context={},
            request_data={},
            instance=s3_request_params.s3_config,
        )
        params = await validators.S3RequestParamsValidator()(
            value=s3_request_params,
            context={},
        )
        if not params:
            raise ValueError(
                "Params is `None` after validation!",
            )  # pragma: no cover
        generated_params = await s3_client.async_generate_params(
            filename=params.filename,
            config=params.s3_config,
            content_type=params.content_type,
            upload_folder=self.upload_folder,
            extra_metadata=self.get_extra_meta_data(user_data),
        )
        return schemas.S3UploadParams.model_validate(generated_params)

    def get_extra_meta_data(
        self,
        user: core_permissions.UserT,
    ) -> dict[str, str]:
        """Extend meta data for file."""
        return {}  # pragma: no cover
