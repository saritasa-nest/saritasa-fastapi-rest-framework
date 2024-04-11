import collections.abc
import enum
import functools
import typing

import fastapi
import pydantic

from .. import metrics, permissions, repositories
from . import core, filters, schemas, types


class PaginationParams(
    pydantic.BaseModel,
    typing.Generic[filters.FiltersT],
):
    """Define base pagination params."""

    filters: filters.FiltersT
    order_by: list[enum.StrEnum]
    offset: int = pydantic.Field(
        fastapi.Query(
            default=0,
            ge=0,
        ),
    )
    limit: int


class ListMixin(
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
        types.ListSchema,
        filters.FiltersT,
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
    """Add list endpoint to api."""

    filter: type[filters.FiltersT]
    list_schema: type[types.ListSchema]
    list_limit_default: int = 25
    list_limit_max: int = 100
    ordering_fields: collections.abc.Sequence[str]

    @property
    def filters_dependency(
        self,
    ) -> type[filters.FiltersT]:
        """Prepare filters dependency."""
        return typing.Annotated[  # type: ignore
            self.filter,
            fastapi.Depends(),
        ]

    def list(
        self,
    ) -> collections.abc.Callable[
        ...,
        collections.abc.Coroutine[
            typing.Any,
            typing.Any,
            schemas.PaginatedResult[types.ListSchema],
        ],
    ]:
        """Prepare list endpoint."""
        return self.prepare_list(
            user_dependency=self.user_dependency,
            repository_dependency=self.repository_dependency,
            context_dependency=self.context_dependency,
            list_schema=self.list_schema,
            pagination_dependency=self.get_pagination_dependency(
                ordering_enum=self.get_ordering_enum(self.ordering_fields),
                filters_dependency=self.filters_dependency,
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
            permissions=self.get_permissions(
                action=self.action,
            ),
        )

    def prepare_list(
        self,
        list_schema: type[types.ListSchema],
        user_dependency: type[permissions.UserT],
        repository_dependency: type[repositories.ApiRepositoryProtocolT],
        context_dependency: type[types.Context],
        pagination_dependency: type[PaginationParams[filters.FiltersT]],
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
            schemas.PaginatedResult[types.ListSchema],
        ],
    ]:
        """Prepare list endpoint."""

        async def _list(
            user: user_dependency,
            repository: repository_dependency,
            pagination_params: pagination_dependency,
            context: context_dependency,
        ) -> schemas.PaginatedResult[list_schema]:
            await self.check_permissions(
                user=user,
                permissions=permissions,
                context=dict(context),
                request_data=None,
            )
            return await self.perform_list(
                user=user,
                list_schema=list_schema,
                repository=repository,
                context=context,
                joined_load=joined_load,
                select_in_load=select_in_load,
                annotations=annotations,
                pagination_params=pagination_params,
            )

        return _list

    @metrics.tracker
    async def perform_list(
        self,
        user: permissions.UserT,
        list_schema: type[types.ListSchema],
        repository: repositories.ApiRepositoryProtocolT,
        context: types.Context,
        pagination_params: PaginationParams[filters.FiltersT],
        annotations: collections.abc.Sequence[repositories.AnnotationT] = (),
        joined_load: collections.abc.Sequence[repositories.LazyLoadedT] = (),
        select_in_load: collections.abc.Sequence[
            repositories.LazyLoadedT
        ] = (),
    ) -> schemas.PaginatedResult[types.ListSchema]:
        """Prepare  list of instances to be returned in api."""
        results, count = await self.paginate_data(
            user=user,
            repository=repository,
            context=context,
            offset=pagination_params.offset,
            limit=pagination_params.limit,
            order_by=pagination_params.order_by,
            annotations=annotations,
            joined_load=joined_load,
            select_in_load=select_in_load,
            where=await pagination_params.filters.to_filters(
                user=user,
                context=dict(context),
            ),
        )

        model_validate = functools.partial(
            list_schema.model_validate,
            context=dict(context),
        )
        return schemas.PaginatedResult[types.ListSchema](
            count=count,
            results=list(map(model_validate, results)),
        )

    @metrics.tracker
    def get_ordering_enum(
        self,
        ordering_fields: collections.abc.Sequence[str],
    ) -> type[enum.StrEnum]:
        """Prepare ordering enum."""
        return enum.StrEnum(  # type: ignore # pragma: no cover
            "OrderingEnum",
            ordering_fields,
        )

    @metrics.tracker
    def prepare_pagination_params(
        self,
        ordering_enum: type[enum.StrEnum],
        filters_dependency: type[filters.FiltersT],
    ) -> type[PaginationParams[filters.FiltersT]]:
        """Prepare pagination parameters."""

        class GeneratedPaginationParams(
            PaginationParams[filters.FiltersT],  # type: ignore
        ):
            """Generated params for list endpoint."""

            filters: filters_dependency
            order_by: list[ordering_enum] = pydantic.Field(
                fastapi.Query(default_factory=list),
            )
            limit: int = pydantic.Field(
                fastapi.Query(
                    default=self.list_limit_default,
                    ge=0,
                    le=self.list_limit_max,
                ),
            )

        return GeneratedPaginationParams

    @metrics.tracker
    def get_pagination_dependency(
        self,
        ordering_enum: type[enum.StrEnum],
        filters_dependency: type[filters.FiltersT],
    ) -> type[PaginationParams[filters.FiltersT]]:
        """Prepare pagination params dependency."""
        return typing.Annotated[  # type: ignore
            self.prepare_pagination_params(
                ordering_enum=ordering_enum,
                filters_dependency=filters_dependency,
            ),
            fastapi.Depends(),
        ]
