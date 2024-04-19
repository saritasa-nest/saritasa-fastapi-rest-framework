import typing

import saritasa_s3_tools

from .. import common_types, exceptions, permissions


class S3ConfigPermission(
    permissions.BasePermission[
        saritasa_s3_tools.S3FileTypeConfig,
        permissions.UserT,
    ],
    typing.Generic[permissions.UserT,],
):
    """Check that user is allowed to use s3 config."""

    async def _check_instance_permission(
        self,
        user: permissions.UserT,
        action: str,
        instance: saritasa_s3_tools.S3FileTypeConfig,
        context: common_types.ContextType,
        request_data: permissions.RequestData,
    ) -> None:
        """Check that user has permission for s3 config."""
        if instance.auth and not instance.auth(user):
            raise exceptions.PermissionException(
                detail="User can't use this config for upload",
            )
