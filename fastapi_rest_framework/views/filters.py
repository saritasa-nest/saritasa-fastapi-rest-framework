import collections.abc
import typing

import pydantic

from .. import common_types, permissions, repositories


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

    def transform_search(
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

    def transform_filter(
        self,
        user: permissions.UserT,
        model: type[repositories.APIModelT],
        api_filter: str,
        value: typing.Any,
        context: common_types.ContextType,
    ) -> repositories.WhereFilterT:
        """Prepare filter."""
        raise NotImplementedError  # pragma: no cover

    async def to_filters(
        self,
        user: permissions.UserT,
        context: common_types.ContextType,
    ) -> list[repositories.WhereFilterT]:
        """Transform model into proper filters."""
        filters_mapping = self.model_dump(mode="python")
        filters = []
        for api_filter, value in filters_mapping.items():
            if value is None:
                continue
            if value == "":
                continue
            if isinstance(value, collections.abc.Sized) and len(value) == 0:
                continue
            if hasattr(self, f"transform_{api_filter}"):
                filters.append(
                    getattr(
                        self,
                        f"transform_{api_filter}",
                    )(
                        user,
                        self._model,
                        value,
                        context,
                    ),
                )
                continue
            filters.append(
                self.transform_filter(
                    user,
                    self._model,
                    api_filter,
                    value,
                    context,
                ),
            )
        return filters


AnyFilters = Filters[typing.Any, typing.Any, typing.Any]
FiltersT = typing.TypeVar(
    "FiltersT",
    bound=AnyFilters,
)
