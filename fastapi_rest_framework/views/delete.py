import collections.abc
import typing

from .. import (
    common_types,
    exceptions,
    interactors,
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
            data_interactor=self.data_interactor,  # type: ignore
            permissions=self.get_permissions(
                action=self.action,
            ),
        )

    def prepare_delete(
        self,
        pk_query: type[str] | type[int],
        repository_dependency: type[repositories.ApiRepositoryProtocolT],
        user_dependency: type[permissions.UserT],
        context_dependency: type[types.Context],
        data_interactor: type[
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
                data_interactor=data_interactor(
                    repository=repository,
                    user=user,
                ),
                instance=instance,
            )

        return delete

    async def perform_delete(
        self,
        user: permissions.UserT,
        context: common_types.ContextType,
        repository: repositories.ApiRepositoryProtocolT,
        data_interactor: interactors.ApiDataInteractor[
            permissions.UserT,
            repositories.SelectStatementT,
            repositories.ApiRepositoryProtocolT,
            repositories.APIModelT,
        ],
        instance: repositories.APIModelT,
    ) -> None:
        """Preform delete operation."""
        await data_interactor.delete(instance=instance, context=context)
