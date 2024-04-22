import mimetypes
import pathlib

import httpx
import saritasa_s3_tools

from .. import testing
from . import schemas, views


async def upload_file_to_s3(
    api_client: httpx.AsyncClient,
    config: str,
    file_path: str,
    s3_params_url: str = "/s3/",
) -> tuple[str, str]:
    """Upload file to s3 and get url and key."""
    response = await api_client.post(
        s3_params_url,
        json=views.S3GetParamsView()
        .generate_request_params_schema()(
            config=config,
            filename=file_path.split("/")[-1],
            content_type=mimetypes.MimeTypes().guess_type(file_path)[0] or "",
            content_length=pathlib.Path(file_path).stat().st_size,
        )
        .model_dump(mode="json"),
    )
    response_data = testing.extract_schema_from_response(
        response=response,
        schema=schemas.S3UploadParams,
    )
    return saritasa_s3_tools.testing.upload_file_and_verify(
        filepath=file_path,
        s3_params=saritasa_s3_tools.client.S3UploadParams(
            url=str(response_data.url),
            params=dict(response_data.params),
        ),
    )


async def check_s3_url_is_valid(url: str) -> None:
    """Ensure that response from request to S3 URL is success."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    assert response.is_success, response.content


async def check_s3_key_is_valid(
    s3_client: saritasa_s3_tools.AsyncS3Client,
    key: str,
) -> bool:
    """Ensure that response from request to S3 URL is success."""
    return await s3_client.async_is_file_in_bucket(key)
