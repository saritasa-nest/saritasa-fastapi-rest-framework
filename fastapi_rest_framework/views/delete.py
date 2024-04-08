import collections.abc
import typing

from .. import (
    common_types,
    exceptions,
    interactors,
    metrics,
    permissions,
    repositories,
)
from . import core, types


class DeleteMixin(
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
    """Add delete endpoint to API."""

    def delete(
        self,
    ) -> collections.abc.Callable[
        ...,
        collections.abc.Coroutine[typing.Any, typing.Any, None],
    ]:
        """Prepare delete endpoint."""
        return self.prepare_delete(
            pk_query=self.pk_attr_query_type,
            user_dependency=self.user_dependency,
            repository_dependency=self.repository_dependency,
            context_dependency=self.context_dependency,
            interactor=self.interactor,  # type: ignore
            permissions=self.get_permissions(
                action=self.action,
            ),
            annotations=self.get_annotations(
                action=self.action,
            ),
            joined_load=self.get_joined_load_options(
                action=self.action,
            ),
            select_in_load=self.get_select_in_load_options(
                action=self.action,
            ),
        )

    def prepare_delete(
        self,
        pk_query: type[str] | type[int],
        repository_dependency: type[repositories.ApiRepositoryProtocolT],
        user_dependency: type[permissions.UserT],
        context_dependency: type[types.Context],
        interactor: type[
            interactors.ApiDataInteractor[
                permissions.UserT,
                repositories.SelectStatementT,
                repositories.ApiRepositoryProtocolT,
                repositories.APIModelT,
            ]
        ],
        permissions: collections.abc.Sequence[
            permissions.BasePermission[
                repositories.APIModelT,
                permissions.UserT,
            ]
        ] = (),
        annotations: collections.abc.Sequence[repositories.AnnotationT] = (),
        joined_load: collections.abc.Sequence[repositories.LazyLoadedT] = (),
        select_in_load: collections.abc.Sequence[
            repositories.LazyLoadedT
        ] = (),
    ) -> collections.abc.Callable[
        ...,
        collections.abc.Coroutine[typing.Any, typing.Any, None],
    ]:
        """Prepare delete endpoint."""

        async def delete(
            pk: pk_query,
            user: user_dependency,
            repository: repository_dependency,
            context: context_dependency,
        ) -> None:
            instance = await self.get_object(
                pk=pk,
                user=user,
                repository=repository,
                annotations=annotations,
                joined_load=joined_load,
                select_in_load=select_in_load,
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
            return await self.perform_delete(
                user=user,
                context=dict(context),
                repository=repository,
                interactor=interactor(
                    repository=repository,
                    user=user,
                ),
                instance=instance,
            )

        return delete

    @metrics.tracker
    async def perform_delete(
        self,
        user: permissions.UserT,
        context: common_types.ContextType,
        repository: repositories.ApiRepositoryProtocolT,
        interactor: interactors.ApiDataInteractor[
            permissions.UserT,
            repositories.SelectStatementT,
            repositories.ApiRepositoryProtocolT,
            repositories.APIModelT,
        ],
        instance: repositories.APIModelT,
    ) -> None:
        """Preform delete operation."""
        await interactor.delete(instance=instance, context=context)
