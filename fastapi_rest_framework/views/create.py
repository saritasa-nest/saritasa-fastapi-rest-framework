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


class CreateMixin(
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
        types.CreateSchema,
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
    """Add create endpoint to API."""

    create_detail_schema: type[types.DetailSchema]
    create_schema: type[types.CreateSchema]

    def create(
        self,
    ) -> collections.abc.Callable[
        ...,
        collections.abc.Coroutine[
            typing.Any,
            typing.Any,
            types.DetailSchema,
        ],
    ]:
        """Prepare create endpoint."""
        if hasattr(self, "create_detail_schema"):
            create_detail_schema = self.create_detail_schema
        elif hasattr(self, "detail_schema"):
            create_detail_schema = self.detail_schema  # type: ignore
        else:
            raise ValueError(  # pragma: no cover
                (
                    "Please set `create_detail_schema` or `detail_schema`"
                    f"for {self.__class__}"
                ),
            )
        validator = self.get_validator(action=self.action)
        if issubclass(validator, validators.BaseModelListValidator):
            raise ValueError(  # pragma: no cover
                (
                    "List validator is not supported in `update` action"
                    f"for {self.__class__}"
                ),
            )
        return self.prepare_create(
            create_schema=self.create_schema,
            create_detail_schema=create_detail_schema,
            user_dependency=self.user_dependency,
            repository_dependency=self.repository_dependency,
            context_dependency=self.context_dependency,
            interactor=self.interactor,  # type: ignore
            annotations=self.get_annotations(
                action=self.action,
            ),
            validator=validator,
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

    def prepare_create(
        self,
        create_schema: type[types.CreateSchema],
        create_detail_schema: type[types.DetailSchema],
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
        """Prepare create endpoint."""

        async def create(
            request: create_schema,
            user: user_dependency,
            repository: repository_dependency,
            context: context_dependency,
        ) -> create_detail_schema:
            context_dump: common_types.ContextType = dict(context)
            await self.check_permissions(
                user=user,
                permissions=permissions,
                context=context_dump,
                request_data=dict(request),
            )
            validated_data = await self.validate_data(
                context=context_dump,
                model=request,
                validator=validator,
                repository=repository,
            )
            return await self.perform_create(
                user=user,
                context=context_dump,
                schema=create_detail_schema,
                repository=repository,
                interactor=interactor(
                    repository=repository,
                    user=user,
                ),
                validated_data=validated_data,
                annotations=annotations,
                joined_load=joined_load,
                select_in_load=select_in_load,
            )

        return create

    async def perform_create(
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
        """Perform create operation."""
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
