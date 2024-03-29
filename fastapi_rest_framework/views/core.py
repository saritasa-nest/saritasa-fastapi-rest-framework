import collections.abc
import enum
import http
import inspect
import typing

import fastapi
import pydantic

from .. import (
    common_types,
    exceptions,
    interactors,
    permissions,
    repositories,
    validators,
)
from . import constants, types


class BaseAPIViewMeta(type):
    """Metaclass for BaseAPIView."""

    def __new__(
        cls,
        name,  # noqa: ANN001
        bases,  # noqa: ANN001
        attrs,  # noqa: ANN001
        **kwargs,
    ) -> type["AnyBaseAPIView"]:
        """Register endpoint in router."""
        obj_cls: type[AnyBaseAPIView] = super().__new__(
            cls,  # type: ignore
            name,
            bases,
            attrs,
            **kwargs,
        )
        if name == "BaseAPIView":
            return obj_cls
        if not hasattr(obj_cls, "router"):
            return obj_cls
        for attr in (
            "repository_class",
            "model",
        ):
            if not hasattr(obj_cls, attr):
                raise ValueError(  # pragma: no cover
                    f"Please set {attr} in {name}",
                )
        obj_cls.joined_load_map = getattr(  # type: ignore
            obj_cls,
            "joined_load_map",
            {},
        )
        obj_cls.select_in_load_map = getattr(  # type: ignore
            obj_cls,
            "select_in_load_map",
            {},
        )
        obj_cls.annotations_map = getattr(  # type: ignore
            obj_cls,
            "annotations_map",
            {},
        )
        obj_cls.permission_map = getattr(  # type: ignore
            obj_cls,
            "permission_map",
            {},
        )
        obj_cls.validators_map = getattr(  # type: ignore
            obj_cls,
            "validators_map",
            {},
        )
        obj_cls.router_kwargs_map = getattr(
            obj_cls,
            "router_kwargs_map",
            {},
        )
        if not getattr(obj_cls, "interactor", None):

            class DefaultInteractor(
                interactors.ApiDataInteractor[  # type: ignore
                    typing.Any,
                    typing.Any,
                    obj_cls.repository_class,  # type: ignore
                    obj_cls.model,  # type: ignore
                ],
            ):
                model = obj_cls.model  # type: ignore

            obj_cls.interactor = DefaultInteractor  # type: ignore
        obj_cls.register_endpoints()
        return obj_cls


class BaseAPIViewMixin(
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
    """Base mixin for views and mixins."""

    action: str
    pk_attr: str = "id"
    router: fastapi.APIRouter
    repository_class: type[repositories.ApiRepositoryProtocolT]
    model: type[repositories.APIModelT]
    context: type[types.Context] = types.Context

    # Maps for endpoints are defined in following way:
    # {"method": value}
    # For example: {"list": "value"}
    # If method not present in map, we'll check out 'default' key
    # What model/schema should be return on status code
    responses_map: typing.ClassVar[types.ActionResponsesMap] = {
        "default": constants.DEFAULT_ERROR_RESPONSES,
    }
    # Additional arguments for router endpoint registration
    router_kwargs_map: typing.Mapping[
        str,
        dict[str, typing.Any],
    ]
    # What should be join loaded for object/objects for endpoint
    joined_load_map: typing.Mapping[
        str,
        collections.abc.Sequence[repositories.LazyLoadedT],
    ]
    # What should be separately loaded in for object/objects for endpoint
    select_in_load_map: typing.Mapping[
        str,
        collections.abc.Sequence[repositories.LazyLoadedT],
    ]
    # What annotations should be returned for endpoint
    annotations_map: typing.Mapping[
        str,
        collections.abc.Sequence[repositories.AnnotationT],
    ]
    # Base permissions which will be applied to each endpoint
    base_permissions: collections.abc.Sequence[
        permissions.BasePermission[
            repositories.APIModelT,
            permissions.UserT,
        ]
    ] = ()
    # Permissions for each endpoint
    permission_map: typing.Mapping[
        str,
        collections.abc.Sequence[
            permissions.BasePermission[
                repositories.APIModelT,
                permissions.UserT,
            ]
        ],
    ]
    # Validators for each endpoint(usually create/update)
    validators_map: typing.Mapping[
        str,
        type[
            validators.BaseModelValidator[
                repositories.ApiRepositoryProtocolT,
                repositories.APIModelT,
            ]
        ],
    ]
    # Interactors for each endpoint(usually create/update/delete)
    interactor: type[
        interactors.ApiDataInteractor[
            permissions.UserT,
            repositories.SelectStatementT,
            repositories.ApiRepositoryProtocolT,
            repositories.APIModelT,
        ]
    ]

    @classmethod
    def get_basename(cls) -> str:
        """Get basename of api view.

        It is used to construct each endpoint's name.

        """
        return cls.router.prefix.strip("/")

    @property
    def pk_attr_query_type(self) -> type[str] | type[int]:
        """Get query type for pk field."""
        return typing.Annotated[  # type: ignore
            str,
            fastapi.Path(),
        ]  # pragma: no cover

    @property
    def repository_dependency(
        self,
    ) -> type[repositories.ApiRepositoryProtocolT]:
        """Prepare repository dependency."""
        raise NotImplementedError  # pragma: no cover

    @property
    def user_dependency(self) -> type[permissions.UserT]:
        """Prepare security dependency."""
        raise NotImplementedError  # pragma: no cover

    @property
    def context_dependency(
        self,
    ) -> type[types.Context]:
        """Prepare context dependency."""
        return typing.Annotated[  # type: ignore
            self.context,
            fastapi.Depends(),
        ]

    def get_select_in_load_options(
        self,
        action: str = "default",
    ) -> collections.abc.Sequence[repositories.LazyLoadedT]:
        """Get selectinload options for endpoint."""
        if action not in self.select_in_load_map:
            return self.select_in_load_map.get("default", ())
        return self.select_in_load_map[action]

    def get_joined_load_options(
        self,
        action: str = "default",
    ) -> collections.abc.Sequence[repositories.LazyLoadedT]:
        """Get joinedload options for endpoint."""
        if action not in self.joined_load_map:
            return self.joined_load_map.get("default", ())
        return self.joined_load_map[action]

    def get_annotations(
        self,
        action: str = "default",
    ) -> collections.abc.Sequence[repositories.AnnotationT]:
        """Get annotations for endpoint."""
        if action not in self.annotations_map:
            return self.annotations_map.get("default", ())
        return self.annotations_map[action]

    def get_permissions(
        self,
        action: str = "default",
    ) -> collections.abc.Sequence[
        permissions.BasePermission[repositories.APIModelT, permissions.UserT]
    ]:
        """Get permissions for endpoint."""
        if action not in self.permission_map:
            return self.permission_map.get("default", ())
        return self.permission_map[action]

    def get_validator(
        self,
        action: str = "default",
    ) -> type[
        validators.BaseModelValidator[
            repositories.ApiRepositoryProtocolT,
            repositories.APIModelT,
        ]
    ]:
        """Get validator for endpoint."""
        if action not in self.validators_map:

            class DefaultValidator(
                validators.BaseModelValidator[
                    self.repository_class,  # type: ignore
                    self.model,  # type: ignore
                ],
            ):
                model: type[repositories.APIModelT] = self.model

            return self.validators_map.get("default", DefaultValidator)
        return self.validators_map[action]

    def get_responses(
        self,
        action: str = "default",
    ) -> dict[int | str, dict[str, typing.Any]]:
        """Get responses for endpoint."""
        if action not in self.responses_map:
            return self.responses_map.get("default", {})
        return self.responses_map[action]

    async def get_filters_values(
        self,
        user: permissions.UserT,
        repository: repositories.ApiRepositoryProtocolT,
        where: collections.abc.Sequence[repositories.WhereFilterT],
        **filters_by: typing.Any,
    ) -> tuple[
        collections.abc.Sequence[repositories.WhereFilterT],
        dict[str, typing.Any],
    ]:
        """Prepare filters values for filtration."""
        if "pk" in filters_by:
            pk_value = filters_by.pop("pk")
            filters_by[self.pk_attr] = pk_value
        return where, filters_by

    async def prepare_fetch_statement(
        self,
        user: permissions.UserT,
        repository: repositories.ApiRepositoryProtocolT,
        offset: int = 0,
        limit: int = 0,
        order_by: collections.abc.Sequence[
            repositories.OrderingClauseT | enum.StrEnum
        ] = (),
        annotations: collections.abc.Sequence[repositories.AnnotationT] = (),
        joined_load: collections.abc.Sequence[repositories.LazyLoadedT] = (),
        select_in_load: collections.abc.Sequence[
            repositories.LazyLoadedT
        ] = (),
        where: collections.abc.Sequence[repositories.WhereFilterT]
        | None = None,
        **filters_by,
    ) -> repositories.SelectStatementT:
        """Prepare fetch statement."""
        where_filter, filters_by = await self.get_filters_values(
            user=user,
            repository=repository,
            where=where or [],
            **filters_by,
        )
        return repository.get_fetch_statement(
            offset=offset,
            limit=limit,
            ordering_clauses=order_by,
            where=where_filter,
            joined_load=joined_load,
            select_in_load=select_in_load,
            annotations=annotations,
            **filters_by,
        )

    async def get_object(
        self,
        pk: int | str | None,
        user: permissions.UserT,
        repository: repositories.ApiRepositoryProtocolT,
        annotations: collections.abc.Sequence[repositories.AnnotationT] = (),
        joined_load: collections.abc.Sequence[repositories.LazyLoadedT] = (),
        select_in_load: collections.abc.Sequence[
            repositories.LazyLoadedT
        ] = (),
    ) -> repositories.APIModelT | None:
        """Load object from database."""
        return await repository.fetch_first(
            statement=await self.prepare_fetch_statement(
                user=user,
                pk=pk,
                repository=repository,
                joined_load=joined_load,
                select_in_load=select_in_load,
                annotations=annotations,
            ),
        )

    async def paginate_data(
        self,
        user: permissions.UserT,
        repository: repositories.ApiRepositoryProtocolT,
        context: types.Context,
        offset: int,
        limit: int,
        order_by: collections.abc.Sequence[
            repositories.OrderingClauseT | enum.StrEnum
        ],
        annotations: collections.abc.Sequence[repositories.AnnotationT],
        joined_load: collections.abc.Sequence[repositories.LazyLoadedT] = (),
        select_in_load: collections.abc.Sequence[
            repositories.LazyLoadedT
        ] = (),
        where: collections.abc.Sequence[repositories.WhereFilterT]
        | None = None,
        **filters_by,
    ) -> tuple[collections.abc.Sequence[repositories.APIModelT], int]:
        """Load paginated data from database."""
        objects = await repository.fetch_all(
            statement=await self.prepare_fetch_statement(
                user=user,
                repository=repository,
                offset=offset,
                limit=limit,
                order_by=order_by,
                where=where,
                joined_load=joined_load,
                select_in_load=select_in_load,
                annotations=annotations,
                **filters_by,
            ),
        )
        where_filter, filters_by = await self.get_filters_values(
            user=user,
            repository=repository,
            where=where or [],
            **filters_by,
        )
        count = await repository.count(
            where=where_filter,
            **filters_by,
        )
        return objects, count

    async def check_permissions(
        self,
        user: permissions.UserT,
        permissions: collections.abc.Sequence[
            permissions.BasePermission[
                repositories.APIModelT,
                permissions.UserT,
            ]
        ],
        context: common_types.ContextType,
        request_data: permissions.RequestData,
        instance: repositories.APIModelT | None = None,
    ) -> None:
        """Check permissions."""
        for permission in self.base_permissions:
            await permission(
                user=user,
                action=self.action,
                instance=instance,
                context=context,
                request_data=request_data,
            )
        for permission in permissions:
            await permission(
                user=user,
                action=self.action,
                instance=instance,
                context=context,
                request_data=request_data,
            )

    async def validate_data(
        self,
        context: common_types.ContextType,
        model: pydantic.BaseModel,
        validator: type[
            validators.BaseModelValidator[
                repositories.ApiRepositoryProtocolT,
                repositories.APIModelT,
            ]
        ],
        repository: repositories.ApiRepositoryProtocolT,
        instance: repositories.APIModelT | None = None,
    ) -> validators.ApiDataType:
        """Validate data."""
        validated_data = await validator(
            repository=repository,
            instance=instance,
        )(
            value=model.model_dump(),
            context=context,
        )
        return validated_data or {}


class BaseAPIView(
    BaseAPIViewMixin[
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
    metaclass=BaseAPIViewMeta,
):
    """Base api view."""

    @classmethod
    def register_endpoints(cls) -> None:
        """Register endpoint in router."""
        for name, func in cls.__dict__.items():
            if not hasattr(func, "action_config"):
                continue
            endpoint = cls()
            endpoint.action = name.replace("_", "-")
            detail = func.action_config["detail"]
            paginated = func.action_config["paginated"]

            getattr(cls.router, func.action_config["method"])(
                (
                    f"/{{pk}}/{endpoint.action}/"
                    if detail
                    else f"/{endpoint.action}/"
                ),
                name=f"{cls.get_basename()}-{endpoint.action}",
                status_code=func.action_config["status_code"],
                response_class=func.action_config["response_class"],
                responses=endpoint.get_responses(action=endpoint.action),
                **endpoint.router_kwargs_map.get(endpoint.action, {}),
            )(
                endpoint.prepare_action(func, detail, paginated),
            )

        if hasattr(cls, "list"):
            endpoint = cls()
            endpoint.action = "list"
            cls.router.get(
                "/",
                name=f"{cls.get_basename()}-{endpoint.action}",
                responses=endpoint.get_responses(action=endpoint.action),
                **endpoint.router_kwargs_map.get(endpoint.action, {}),
            )(
                endpoint.list(),  # type: ignore
            )
        if hasattr(cls, "detail"):
            endpoint = cls()
            endpoint.action = "detail"
            cls.router.get(
                "/{pk}/",
                name=f"{cls.get_basename()}-{endpoint.action}",
                responses=endpoint.get_responses(action=endpoint.action),
                **endpoint.router_kwargs_map.get(endpoint.action, {}),
            )(
                endpoint.detail(),  # type: ignore
            )
        if hasattr(cls, "create"):
            endpoint = cls()
            endpoint.action = "create"
            cls.router.post(
                "/",
                name=f"{cls.get_basename()}-{endpoint.action}",
                status_code=http.HTTPStatus.CREATED,
                responses=endpoint.get_responses(action=endpoint.action),
                **endpoint.router_kwargs_map.get(endpoint.action, {}),
            )(
                endpoint.create(),  # type: ignore
            )
        if hasattr(cls, "update"):
            endpoint = cls()
            endpoint.action = "update"
            cls.router.put(
                "/{pk}/",
                name=f"{cls.get_basename()}-{endpoint.action}",
                responses=endpoint.get_responses(action=endpoint.action),
                **endpoint.router_kwargs_map.get(endpoint.action, {}),
            )(
                endpoint.update(),  # type: ignore
            )
        if hasattr(cls, "delete"):
            endpoint = cls()
            endpoint.action = "delete"
            cls.router.delete(
                "/{pk}/",
                name=f"{cls.get_basename()}-{endpoint.action}",
                status_code=http.HTTPStatus.NO_CONTENT,
                response_class=fastapi.Response,
                responses=endpoint.get_responses(action=endpoint.action),
                **endpoint.router_kwargs_map.get(endpoint.action, {}),
            )(
                endpoint.delete(),  # type: ignore
            )

    def prepare_action_context(
        self,
        func: collections.abc.Callable[..., typing.Any],
        detail: bool,
        paginated: bool,
    ) -> type[pydantic.BaseModel]:
        """Prepare action context."""
        action_dependencies = {}
        if paginated:
            action_dependencies["pagination_params"] = (
                self.get_pagination_dependency(  # type: ignore
                    ordering_enum=self.get_ordering_enum(  # type: ignore
                        self.ordering_fields,  # type: ignore
                    ),
                    filters_dependency=self.filters_dependency,  # type: ignore
                ),
                ...,
            )
        inspected_func = inspect.signature(func)
        action_dependencies.update(
            **{
                arg: (
                    parameter.annotation,
                    (
                        parameter.default
                        if not isinstance(
                            parameter.default,
                            inspect._empty,
                        )
                        else ...
                    ),
                )
                for arg, parameter in inspected_func.parameters.items()
                if arg
                not in (  # They will be provided by default
                    "self",
                    "user",
                    "repository",
                    "instance",
                    "context",
                    "validator",
                    "interactor",
                    "joined_load",
                    "select_in_load",
                    "annotations",
                    "reload_fetch_statement",
                    "pagination_params",
                    "return",  # Ignore return
                    "kwargs",
                )
            },  # type: ignore
        )
        action_context_class = pydantic.create_model(
            "ActionContext",
            __base__=pydantic.BaseModel,
            **action_dependencies,  # type: ignore
        )
        return action_context_class

    def prepare_action(
        self,
        func: collections.abc.Callable[..., typing.Any],
        detail: bool,
        paginated: bool,
    ) -> collections.abc.Callable[..., typing.Any]:
        """Prepare action endpoint."""
        action_context_class = self.prepare_action_context(
            func=func,
            detail=detail,
            paginated=paginated,
        )
        func_return = func.__annotations__["return"]

        async def action(
            action_context: typing.Annotated[  # type: ignore
                action_context_class,  # type: ignore
                fastapi.Depends(),
            ],
            user: self.user_dependency,  # type: ignore
            repository: self.repository_dependency,  # type: ignore
            context: self.context_dependency,  # type: ignore
        ) -> func_return:  # type: ignore
            context_dump: common_types.ContextType = dict(context)
            request_context_dump: common_types.ContextType = dict(
                action_context,
            )
            request_data: permissions.RequestData = None
            if "request" in request_context_dump:
                request_data = dict(request_context_dump["request"])
            await self.check_permissions(
                user=user,
                permissions=self.get_permissions(
                    action=self.action,
                ),
                context=context_dump,
                request_data=request_data,
            )
            return await func(
                self,
                repository=repository,
                context=context,
                user=user,
                validator=self.get_validator(
                    action=self.action,
                ),
                interactor=self.interactor,
                joined_load=self.get_joined_load_options(
                    action=self.action,
                ),
                select_in_load=self.get_select_in_load_options(
                    action=self.action,
                ),
                annotations=self.get_annotations(
                    action=self.action,
                ),
                reload_fetch_statement=await self.prepare_fetch_statement(
                    user=user,
                    repository=repository,
                    joined_load=self.get_joined_load_options(
                        action=self.action,
                    ),
                    select_in_load=self.get_select_in_load_options(
                        action=self.action,
                    ),
                    annotations=self.get_annotations(
                        action=self.action,
                    ),
                ),
                **request_context_dump,
            )

        if not detail:
            return action

        async def action_detail(
            pk: int,
            action_context: typing.Annotated[  # type: ignore
                action_context_class,  # type: ignore
                fastapi.Depends(),
            ],
            user: self.user_dependency,  # type: ignore
            repository: self.repository_dependency,  # type: ignore
            context: self.context_dependency,  # type: ignore
        ) -> func_return:  # type: ignore
            context_dump: common_types.ContextType = dict(
                context,
            )
            request_context_dump: common_types.ContextType = dict(
                action_context,
            )
            instance = await self.get_object(
                pk,
                user=user,
                repository=repository,
                joined_load=self.get_joined_load_options(
                    action=self.action,
                ),
                select_in_load=self.get_select_in_load_options(
                    action=self.action,
                ),
                annotations=self.get_annotations(
                    action=self.action,
                ),
            )
            request_data: permissions.RequestData = None
            if "request" in request_context_dump:
                request_data = dict(request_context_dump["request"])
            await self.check_permissions(
                user=user,
                permissions=self.get_permissions(
                    action=self.action,
                ),
                instance=instance,
                context=context_dump,
                request_data=request_data,
            )
            if not instance:
                raise exceptions.NotFoundException()
            return await func(
                self,
                repository=repository,
                user=user,
                instance=instance,
                context=context,
                validator=self.get_validator(
                    action=self.action,
                ),
                interactor=self.interactor,
                joined_load=self.get_joined_load_options(
                    action=self.action,
                ),
                select_in_load=self.get_select_in_load_options(
                    action=self.action,
                ),
                annotations=self.get_annotations(
                    action=self.action,
                ),
                reload_fetch_statement=await self.prepare_fetch_statement(
                    user=user,
                    repository=repository,
                    joined_load=self.get_joined_load_options(
                        action=self.action,
                    ),
                    select_in_load=self.get_select_in_load_options(
                        action=self.action,
                    ),
                    annotations=self.get_annotations(
                        action=self.action,
                    ),
                ),
                **request_context_dump,
            )

        return action_detail


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
