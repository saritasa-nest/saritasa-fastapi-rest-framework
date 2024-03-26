import typing

import saritasa_sqlalchemy_tools

import fastapi_rest_framework

from .. import db, security


class BaseView(
    fastapi_rest_framework.sqlalchemy.SqlAlchemyView[
        security.UserJWTData,
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """Base view for sqlalchemy."""

    @property
    def user_dependency(self) -> type[security.UserJWTData]:
        """Prepare security dependency."""
        return security.UserAuth  # type: ignore

    @property
    def db_session_dependency(
        self,
    ) -> type[saritasa_sqlalchemy_tools.Session]:
        """Prepare repository dependency."""
        return db.get_db_session  # type: ignore


class ListMixin(
    fastapi_rest_framework.sqlalchemy.ListMixin[
        fastapi_rest_framework.ListSchema,
        fastapi_rest_framework.FiltersT,
        security.UserJWTData,
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        fastapi_rest_framework.ListSchema,
        fastapi_rest_framework.FiltersT,
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """List mixin for sqlalchemy."""


class DetailMixin(
    fastapi_rest_framework.sqlalchemy.DetailMixin[
        fastapi_rest_framework.DetailSchema,
        security.UserJWTData,
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        fastapi_rest_framework.DetailSchema,
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """Detail mixin for sqlalchemy."""


class CreateMixin(
    fastapi_rest_framework.sqlalchemy.CreateMixin[
        fastapi_rest_framework.CreateSchema,
        fastapi_rest_framework.DetailSchema,
        security.UserJWTData,
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        fastapi_rest_framework.CreateSchema,
        fastapi_rest_framework.DetailSchema,
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """Create mixin for sqlalchemy."""


class UpdateMixin(
    fastapi_rest_framework.sqlalchemy.UpdateMixin[
        fastapi_rest_framework.UpdateSchema,
        fastapi_rest_framework.DetailSchema,
        security.UserJWTData,
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        fastapi_rest_framework.UpdateSchema,
        fastapi_rest_framework.DetailSchema,
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """Update mixin for sqlalchemy."""


class DeleteMixin(
    fastapi_rest_framework.sqlalchemy.DeleteMixin[
        security.UserJWTData,
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """Update mixin for sqlalchemy."""


class Filters(
    fastapi_rest_framework.sqlalchemy.SQLAlchemyFilters[
        security.UserJWTData,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[saritasa_sqlalchemy_tools.BaseModelT,],
):
    """Filters for SQLAlchemy."""
