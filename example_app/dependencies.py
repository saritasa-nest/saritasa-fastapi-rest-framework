import typing

import botocore.credentials
import fastapi
import pydantic
import saritasa_s3_tools

from . import config


def get_s3_client() -> saritasa_s3_tools.AsyncS3Client:
    """Get s3 client."""
    s3_boto3_client = saritasa_s3_tools.client.get_boto3_s3_client(
        region=config.aws_region,
        s3_endpoint_url_getter=lambda: config.aws_endpoint,
        access_key_getter=lambda: botocore.credentials.Credentials(
            access_key=config.aws_access_key,
            secret_key=config.aws_secret_key,
        ),
    )
    return saritasa_s3_tools.AsyncS3Client(
        boto3_client=s3_boto3_client,
        default_bucket=config.s3_bucket,
    )


S3ClientDependencyType: typing.TypeAlias = pydantic.SkipValidation[
    typing.Annotated[
        saritasa_s3_tools.AsyncS3Client,
        fastapi.Depends(get_s3_client),
    ]
]
