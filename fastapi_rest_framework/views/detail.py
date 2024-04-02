import collections.abc
import typing

from .. import exceptions, metrics, permissions, repositories
from . import core, types


class DetailMixin(
    core.BaseAPIViewMixin[
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
        types.DetailSchema,
        repositories.LazyLoadedT,
        repositories.SelectStatementT,
        repositories.AnnotationT,
        repositories.WhereFilterT,
        repositories.OrderingClauseT,
        permissions.UserT,
        repositories.ApiRepositoryProtocolT,
        repositories.APIModelT,
    ],
):
    """Add detail endpoint to API."""

    detail_schema: type[types.DetailSchema]

    def detail(
        self,
    ) -> collections.abc.Callable[
        ...,
        collections.abc.Coroutine[
            typing.Any,
            typing.Any,
            types.DetailSchema,
        ],
    ]:
        """Prepare detail endpoint."""
        return self.prepare_detail(
            pk_query=self.pk_attr_query_type,
            user_dependency=self.user_dependency,
            repository_dependency=self.repository_dependency,
            context_dependency=self.context_dependency,
            detail_schema=self.detail_schema,
            joined_load=self.get_joined_load_options(
                action=self.action,
            ),
            select_in_load=self.get_select_in_load_options(
                action=self.action,
            ),
            annotations=self.get_annotations(
                action=self.action,
            ),
            permissions=self.get_permissions(
                action=self.action,
            ),
        )

    def prepare_detail(
        self,
        pk_query: type[int] | type[str],
        detail_schema: type[types.DetailSchema],
        user_dependency: type[permissions.UserT],
        repository_dependency: type[repositories.ApiRepositoryProtocolT],
        context_dependency: type[types.Context],
        annotations: collections.abc.Sequence[repositories.AnnotationT] = (),
        joined_load: collections.abc.Sequence[repositories.LazyLoadedT] = (),
        select_in_load: collections.abc.Sequence[
            repositories.LazyLoadedT
        ] = (),
        permissions: collections.abc.Sequence[
            permissions.BasePermission[
                repositories.APIModelT,
                permissions.UserT,
            ]
        ] = (),
    ) -> collections.abc.Callable[
        ...,
        collections.abc.Coroutine[
            typing.Any,
            typing.Any,
            types.DetailSchema,
        ],
    ]:
        """Prepare detail endpoint."""

        async def detail(
            pk: pk_query,
            user: user_dependency,
            repository: repository_dependency,
            context: context_dependency,
        ) -> detail_schema:
            instance = await self.get_object(
                user=user,
                pk=pk,
                repository=repository,
                joined_load=joined_load,
                select_in_load=select_in_load,
                annotations=annotations,
            )
            await self.check_permissions(
                user=user,
                permissions=permissions,
                instance=instance,
                context=dict(context),
                request_data=None,
            )
            if not instance:
                raise exceptions.NotFoundException()
            return await self.perform_detail(
                user=user,
                detail_schema=detail_schema,
                instance=instance,
                context=context,
            )

        return detail

    @metrics.tracker
    async def perform_detail(
        self,
        user: permissions.UserT,
        detail_schema: type[types.DetailSchema],
        instance: repositories.APIModelT,
        context: types.Context,
    ) -> types.DetailSchema:
        """Prepare instance to be returned in api."""
        return detail_schema.model_validate(instance, context=dict(context))
