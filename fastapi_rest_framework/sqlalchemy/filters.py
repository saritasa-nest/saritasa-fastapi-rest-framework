import typing

import saritasa_sqlalchemy_tools

from .. import common_types, permissions, views


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

    def transform_filter(
        self,
        user: permissions.UserT,
        model: type[saritasa_sqlalchemy_tools.BaseModelT],
        api_filter: str,
        value: typing.Any,
        context: common_types.ContextType,
    ) -> saritasa_sqlalchemy_tools.WhereFilter:
        """Create filter instance."""
        return saritasa_sqlalchemy_tools.Filter(
            field=api_filter,
            value=value,
        )
