import collections.abc
import typing

from .. import (
    common_types,
    exceptions,
    interactors,
    permissions,
    repositories,
    validators,
)
from . import core, types


class UpdateMixin(
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
        types.UpdateSchema,
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
    """Add update endpoint to API."""

    update_detail_schema: type[types.DetailSchema]
    update_schema: type[types.UpdateSchema]

    def update(
        self,
    ) -> collections.abc.Callable[
        ...,
        collections.abc.Coroutine[
            typing.Any,
            typing.Any,
            types.DetailSchema,
        ],
    ]:
        """Prepare update endpoint."""
        if hasattr(self, "update_detail_schema"):
            update_detail_schema = self.update_detail_schema
        elif hasattr(self, "detail_schema"):
            update_detail_schema = self.detail_schema  # type: ignore
        else:
            raise ValueError(  # pragma: no cover
                (
                    "Please set `update_detail_schema` or `detail_schema`"
                    f"for {self.__class__}"
                ),
            )
        return self.prepare_update(
            pk_query=self.pk_attr_query_type,
            update_schema=self.update_schema,
            update_detail_schema=update_detail_schema,
            user_dependency=self.user_dependency,
            repository_dependency=self.repository_dependency,
            context_dependency=self.context_dependency,
            interactor=self.interactor,  # type: ignore
            annotations=self.get_annotations(
                action=self.action,
            ),
            validator=self.get_validator(
                action=self.action,
            ),
            permissions=self.get_permissions(
                action=self.action,
            ),
            joined_load=self.get_joined_load_options(
                action=self.action,
            ),
            select_in_load=self.get_select_in_load_options(
                action=self.action,
            ),
        )

    def prepare_update(
        self,
        pk_query: type[str] | type[int],
        update_schema: type[types.UpdateSchema],
        update_detail_schema: type[types.DetailSchema],
        user_dependency: type[permissions.UserT],
        repository_dependency: type[repositories.ApiRepositoryProtocolT],
        context_dependency: type[types.Context],
        interactor: type[
            interactors.ApiDataInteractor[
                permissions.UserT,
                repositories.SelectStatementT,
                repositories.ApiRepositoryProtocolT,
                repositories.APIModelT,
            ]
        ],
        validator: type[
            validators.BaseModelValidator[
                repositories.ApiRepositoryProtocolT,
                repositories.APIModelT,
            ]
        ],
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
        """Prepare update endpoint."""

        async def update(
            pk: pk_query,
            request: update_schema,
            user: user_dependency,
            repository: repository_dependency,
            context: context_dependency,
        ) -> update_detail_schema:
            instance = await self.get_object(
                pk,
                user=user,
                repository=repository,
                joined_load=joined_load,
                select_in_load=select_in_load,
            )
            context_dump: common_types.ContextType = dict(context)
            await self.check_permissions(
                user=user,
                permissions=permissions,
                instance=instance,
                context=context_dump,
                request_data=dict(request),
            )
            if not instance:
                raise exceptions.NotFoundException()
            validated_data = await self.validate_data(
                context=context_dump,
                model=request,
                validator=validator,
                repository=repository,
                instance=instance,
            )
            return await self.perform_update(
                user=user,
                context=context_dump,
                schema=update_detail_schema,
                repository=repository,
                interactor=interactor(
                    repository=repository,
                    user=user,
                    instance=instance,
                ),
                validated_data=validated_data,
                joined_load=joined_load,
                select_in_load=select_in_load,
                annotations=annotations,
            )

        return update

    async def perform_update(
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
        validated_data: validators.ApiDataType,
        schema: type[types.DetailSchema],
        annotations: collections.abc.Sequence[repositories.AnnotationT] = (),
        joined_load: collections.abc.Sequence[repositories.LazyLoadedT] = (),
        select_in_load: collections.abc.Sequence[
            repositories.LazyLoadedT
        ] = (),
    ) -> types.DetailSchema:
        """Perform update operation."""
        # Instance is reloaded from db inside of `interactor.save()`
        instance = await interactor.save(
            data=validated_data,
            context=context,
            reload_fetch_statement=await self.prepare_fetch_statement(
                user=user,
                repository=repository,
                joined_load=joined_load,
                select_in_load=select_in_load,
                annotations=annotations,
            ),
        )
        if not instance:  # pragma: no cover
            raise exceptions.NotFoundException()
        return schema.model_validate(instance, context=context)
