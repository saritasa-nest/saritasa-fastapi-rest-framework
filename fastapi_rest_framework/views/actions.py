import collections.abc
import http
import inspect
import typing

import fastapi
import pydantic

from .. import common_types, exceptions, permissions, repositories
from . import core


def action(
    method: str = http.HTTPMethod.GET,
    detail: bool = False,
    paginated: bool = False,
    status_code: int = http.HTTPStatus.OK,
    response_class: type = fastapi.responses.JSONResponse,
) -> collections.abc.Callable[
    [collections.abc.Callable[..., typing.Any]],
    typing.Any,
]:
    """Add action endpoint to view."""

    def _action(func: collections.abc.Callable[..., typing.Any]) -> typing.Any:
        func.action_config = {  # type: ignore
            "method": method.lower(),
            "detail": detail,
            "paginated": paginated,
            "status_code": status_code,
            "response_class": response_class,
        }
        return func

    return _action


class ActionMixin(
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
    """Add action functionality to view."""

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
        super().register_endpoints()

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
                interactor=self.get_interactor(
                    action=self.action,
                ),
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

        action.__doc__ = func.__doc__
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
                interactor=self.get_interactor(
                    action=self.action,
                ),
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

        action_detail.__doc__ = func.__doc__
        return action_detail
