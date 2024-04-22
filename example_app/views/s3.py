import fastapi
import saritasa_s3_tools

import fastapi_rest_framework

from .. import dependencies, security

saritasa_s3_tools.S3FileTypeConfig(
    name="files",
    key=saritasa_s3_tools.keys.S3KeyWithPrefix("files"),
    allowed=("text/plain",),
    auth=lambda user: bool(user and not user.is_anonymous),
    content_length_range=(5000, 20000000),
)
saritasa_s3_tools.S3FileTypeConfig(
    name="all_file_types",
    key=saritasa_s3_tools.keys.S3KeyWithPrefix("all_file_types"),
    content_length_range=(5000, 20000000),
)
saritasa_s3_tools.S3FileTypeConfig(
    name="all_file_sizes",
    key=saritasa_s3_tools.keys.S3KeyWithPrefix("all_file_sizes"),
)
saritasa_s3_tools.S3FileTypeConfig(
    name="anon_files",
    key=saritasa_s3_tools.keys.S3KeyWithPrefix("anon_files"),
)
saritasa_s3_tools.S3FileTypeConfig(
    name="small_file",
    key=saritasa_s3_tools.keys.S3KeyWithPrefix("small_file"),
    content_length_range=(0, 1),
)
saritasa_s3_tools.S3FileTypeConfig(
    name="images",
    key=saritasa_s3_tools.keys.S3KeyWithPrefix("images"),
    allowed=("image/png",),
    content_length_range=(5000, 20000000),
)


class S3GetParamsView(
    fastapi_rest_framework.s3.S3GetParamsView[
        security.UserAuth,
        dependencies.S3ClientDependencyType,
    ],
):
    """Set up s3 endpoint."""

    router = fastapi.APIRouter(
        prefix="/s3",
        tags=["S3"],
    )
    upload_folder = "upload"
    user_dependency = security.UserAuth  # type: ignore
    s3_client_dependency = dependencies.S3ClientDependencyType

    def get_extra_meta_data(
        self,
        user: security.UserAuth,
    ) -> dict[str, str]:
        """Extend meta data for file."""
        return {
            "user-id": str(user.id),
        }
