import collections.abc
import typing

import saritasa_sqlalchemy_tools
import sqlalchemy

from .. import common_types, metrics, permissions, views


class SQLAlchemyFilters(
    views.Filters[
        saritasa_sqlalchemy_tools.BaseModelT,
        permissions.UserT,
        saritasa_sqlalchemy_tools.WhereFilter,
    ],
    typing.Generic[
        permissions.UserT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """Filters for SQLAlchemy."""

    _transform_search_filter = (
        saritasa_sqlalchemy_tools.transform_search_filter
    )

    def get_group_operator(
        self,
        user: permissions.UserT,
        model: type[saritasa_sqlalchemy_tools.BaseModelT],
        api_filter: str,
        context: common_types.ContextType,
    ) -> collections.abc.Callable[
        ...,
        saritasa_sqlalchemy_tools.SQLWhereFilter,
    ]:
        """Get group operator."""
        return sqlalchemy.and_

    @metrics.tracker
    async def transform_filter(
        self,
        user: permissions.UserT,
        model: type[saritasa_sqlalchemy_tools.BaseModelT],
        api_filter: str,
        value: typing.Any,
        context: common_types.ContextType,
    ) -> saritasa_sqlalchemy_tools.WhereFilter | None:
        """Create filter instance."""
        return saritasa_sqlalchemy_tools.Filter(
            field=api_filter,
            value=value,
        )

    @metrics.tracker
    async def transform_group_filter(
        self,
        user: permissions.UserT,
        model: type[saritasa_sqlalchemy_tools.BaseModelT],
        api_filter: str,
        value: "SQLAlchemyFilters[typing.Any, typing.Any]",
        context: common_types.ContextType,
    ) -> saritasa_sqlalchemy_tools.WhereFilter | None:
        """Prepare group filter."""
        filters: list[saritasa_sqlalchemy_tools.SQLWhereFilter] = []
        for prepared_filter in await value.to_filters(
            user=user,
            context=context,
        ):
            if isinstance(prepared_filter, saritasa_sqlalchemy_tools.Filter):
                filters.append(prepared_filter.transform_filter(value._model))
            else:
                filters.append(prepared_filter)
        if not hasattr(model, api_filter):
            return value.get_group_operator(
                user=user,
                model=model,
                api_filter=api_filter,
                context=context,
            )(*filters)
        field: saritasa_sqlalchemy_tools.ModelAttribute = getattr(
            model,
            api_filter,
        )
        property_filter = field.any if field.property.uselist else field.has
        return property_filter(
            value.get_group_operator(
                user=user,
                model=model,
                api_filter=api_filter,
                context=context,
            )(*filters),
        )
