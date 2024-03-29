import typing

from .. import (
    permissions,
    repositories,
)
from . import actions, core


class BaseAPIView(
    actions.ActionMixin[
        repositories.LazyLoadedT,
        repositories.SelectStatementT,
        repositories.AnnotationT,
        repositories.WhereFilterT,
        repositories.OrderingClauseT,
        permissions.UserT,
        repositories.ApiRepositoryProtocolT,
        repositories.APIModelT,
    ],
    typing.Generic[
        repositories.LazyLoadedT,
        repositories.SelectStatementT,
        repositories.AnnotationT,
        repositories.WhereFilterT,
        repositories.OrderingClauseT,
        permissions.UserT,
        repositories.ApiRepositoryProtocolT,
        repositories.APIModelT,
    ],
    metaclass=core.BaseAPIViewMeta,
):
    """Base api view."""


AnyBaseAPIView = BaseAPIView[
    typing.Any,
    typing.Any,
    typing.Any,
    typing.Any,
    typing.Any,
    typing.Any,
    typing.Any,
    typing.Any,
]
