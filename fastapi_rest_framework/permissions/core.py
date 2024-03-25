import typing

from .. import common_types
from . import types

PermissionInstanceT = typing.TypeVar("PermissionInstanceT", bound=typing.Any)


class BasePermission(
    typing.Generic[
        PermissionInstanceT,
        types.UserT,
    ],
):
    """Base implementation of permissions."""

    async def __call__(
        self,
        user: types.UserT,
        context: common_types.ContextType,
        action: str,
        request_data: types.RequestData,
        instance: PermissionInstanceT | None = None,
    ) -> None:
        """Check permissions."""
        await self._check_permission(
            user=user,
            action=action,
            context=context,
            request_data=request_data,
        )
        if instance:
            await self._check_instance_permission(
                user=user,
                action=action,
                instance=instance,
                context=context,
                request_data=request_data,
            )

    async def _check_permission(
        self,
        user: types.UserT,
        action: str,
        context: common_types.ContextType,
        request_data: types.RequestData,
    ) -> None:
        """Check that user has permission."""

    async def _check_instance_permission(
        self,
        user: types.UserT,
        action: str,
        instance: PermissionInstanceT,
        context: common_types.ContextType,
        request_data: types.RequestData,
    ) -> None:
        """Check that user has permission for instance."""
