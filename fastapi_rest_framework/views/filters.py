import collections.abc
import typing

import pydantic

from .. import common_types, metrics, permissions, repositories


class Filters(
    pydantic.BaseModel,
    typing.Generic[
        repositories.APIModelT,
        permissions.UserT,
        repositories.WhereFilterT,
    ],
):
    """Base model for defying filters.

    To define query param follow this example:

    field__lookup: type = pydantic.Field(fastapi.Query())

    """

    _model: type[repositories.APIModelT]
    _search_fields: collections.abc.Sequence[str]
    _transform_search_filter: collections.abc.Callable[
        [
            type[repositories.APIModelT],
            collections.abc.Sequence[str],
            typing.Any,
        ],
        repositories.WhereFilterT,
    ]
    _api_to_repo_field: typing.ClassVar[dict[str, str]] = {}

    @metrics.tracker
    async def transform_search(
        self,
        user: permissions.UserT,
        model: type[repositories.APIModelT],
        value: typing.Any,
        context: common_types.ContextType,
    ) -> repositories.WhereFilterT:
        """Prepare search filter."""
        return self.__class__._transform_search_filter(
            model,  # type: ignore
            self._search_fields,
            value,
        )

    @metrics.tracker
    async def transform_filter(
        self,
        user: permissions.UserT,
        model: type[repositories.APIModelT],
        api_filter: str,
        value: typing.Any,
        context: common_types.ContextType,
    ) -> repositories.WhereFilterT | None:
        """Prepare filter."""
        raise NotImplementedError  # pragma: no cover

    @metrics.tracker
    async def transform_group_filter(
        self,
        user: permissions.UserT,
        model: type[repositories.APIModelT],
        api_filter: str,
        value: "Filters[typing.Any, typing.Any, typing.Any]",
        context: common_types.ContextType,
    ) -> repositories.WhereFilterT | None:
        """Prepare filter."""
        raise NotImplementedError  # pragma: no cover

    @metrics.tracker
    async def to_filters(
        self,
        user: permissions.UserT,
        context: common_types.ContextType,
    ) -> list[repositories.WhereFilterT]:
        """Transform model into proper filters."""
        filters: list[repositories.WhereFilterT] = []
        for api_filter, value in dict(self).items():
            if (
                value is None
                or value == ""
                or (
                    isinstance(value, collections.abc.Sized)
                    and len(value) == 0
                )
            ):
                continue
            if transform_filter := getattr(
                self,
                f"transform_{api_filter}",
                None,
            ):
                prepared_filter = await transform_filter(
                    user,
                    self._model,
                    value,
                    context,
                )
                if prepared_filter is not None:
                    filters.append(prepared_filter)
                continue
            if isinstance(value, Filters):
                prepared_filter = await self.transform_group_filter(
                    user=user,
                    model=self._model,
                    api_filter=self._api_to_repo_field.get(
                        api_filter,
                        api_filter,
                    ),
                    value=value,
                    context=context,
                )
                if prepared_filter is not None:
                    filters.append(prepared_filter)
                continue
            prepared_filter = await self.transform_filter(
                user=user,
                model=self._model,
                api_filter=self._api_to_repo_field.get(api_filter, api_filter),
                value=value,
                context=context,
            )
            if prepared_filter is not None:
                filters.append(prepared_filter)
        return filters


AnyFilters = Filters[typing.Any, typing.Any, typing.Any]
FiltersT = typing.TypeVar(
    "FiltersT",
    bound=AnyFilters,
)
