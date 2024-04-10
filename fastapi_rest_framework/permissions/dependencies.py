import collections.abc
import typing

import fastapi

from .. import common_types
from . import core, types


def _default_context_dependency() -> common_types.ContextType:
    return {}


DefaultPermissionContextDependency: typing.TypeAlias = typing.Annotated[
    common_types.ContextType,
    fastapi.Depends(_default_context_dependency),
]


def get_permissions_dependency(
    user_dependency: type[types.UserT],
    permissions: collections.abc.Sequence[
        core.BasePermission[typing.Any, typing.Any]
    ],
    action: str = "",
    context_dependency: type[
        common_types.ContextType
    ] = DefaultPermissionContextDependency,  # type: ignore
) -> collections.abc.Callable[
    ...,
    collections.abc.Coroutine[typing.Any, typing.Any, None],
]:
    """Guard endpoint with permissions."""

    async def _permissions_dependency(
        user_data: user_dependency,
        context: context_dependency,
    ) -> None:
        for permission in permissions:
            await permission(
                user=user_data,
                action=action,
                context=context,
                request_data=None,
            )

    return _permissions_dependency
