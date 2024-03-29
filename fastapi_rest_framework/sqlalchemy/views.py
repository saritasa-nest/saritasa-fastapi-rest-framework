import typing

import fastapi
import saritasa_sqlalchemy_tools
import sqlalchemy

from .. import permissions, views
from . import dependencies, repositories


class SqlAlchemyView(
    views.BaseAPIView[
        saritasa_sqlalchemy_tools.LazyLoaded,
        saritasa_sqlalchemy_tools.SelectStatement[
            saritasa_sqlalchemy_tools.BaseModelT
        ],
        saritasa_sqlalchemy_tools.Annotation,
        saritasa_sqlalchemy_tools.WhereFilter,
        saritasa_sqlalchemy_tools.OrderingClause,
        permissions.UserT,
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        permissions.UserT,
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """Base view for sqlalchemy."""

    @property
    def pk_attr_query_type(self) -> type[str] | type[int]:
        """Get query type for pk field."""
        pk_field = getattr(self.model, self.pk_attr)
        match pk_field.type.__class__:
            case sqlalchemy.String:
                return typing.Annotated[  # type: ignore
                    str,
                    fastapi.Path(
                        max_length=pk_field.type.length,
                    ),
                ]
            case sqlalchemy.Integer:
                return typing.Annotated[  # type: ignore
                    int,
                    fastapi.Path(
                        ge=-2147483648,
                        le=2147483647,
                    ),
                ]
            case sqlalchemy.SmallInteger:
                return typing.Annotated[  # type: ignore
                    int,
                    fastapi.Path(
                        ge=-32768,
                        le=32767,
                    ),
                ]
        raise ValueError(  # pragma: no cover
            f"Can't generate query type for {self.pk_attr}",
        )

    @property
    def db_session_dependency(
        self,
    ) -> type[saritasa_sqlalchemy_tools.Session]:
        """Prepare repository dependency."""
        raise NotImplementedError  # pragma: no cover

    @property
    def repository_dependency(
        self,
    ) -> type[repositories.SqlAlchemyRepositoryT]:
        """Prepare repository dependency."""
        return typing.Annotated[  # type: ignore
            self.repository_class,
            fastapi.Depends(
                dependencies.get_repository(
                    repository_class=self.repository_class,
                    session_dependency=self.db_session_dependency,
                ),
            ),
        ]


class ListMixin(
    views.ListMixin[
        views.ListSchema,
        views.FiltersT,
        saritasa_sqlalchemy_tools.LazyLoaded,
        saritasa_sqlalchemy_tools.SelectStatement[
            saritasa_sqlalchemy_tools.BaseModelT
        ],
        saritasa_sqlalchemy_tools.Annotation,
        saritasa_sqlalchemy_tools.WhereFilter,
        saritasa_sqlalchemy_tools.OrderingClause,
        permissions.UserT,
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        views.ListSchema,
        views.FiltersT,
        permissions.UserT,
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """List mixin for sqlalchemy."""


class DetailMixin(
    views.DetailMixin[
        views.DetailSchema,
        saritasa_sqlalchemy_tools.LazyLoaded,
        saritasa_sqlalchemy_tools.SelectStatement[
            saritasa_sqlalchemy_tools.BaseModelT
        ],
        saritasa_sqlalchemy_tools.Annotation,
        saritasa_sqlalchemy_tools.WhereFilter,
        saritasa_sqlalchemy_tools.OrderingClause,
        permissions.UserT,
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        views.DetailSchema,
        permissions.UserT,
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """Detail mixin for sqlalchemy."""


class CreateMixin(
    views.CreateMixin[
        views.CreateSchema,
        views.DetailSchema,
        saritasa_sqlalchemy_tools.LazyLoaded,
        saritasa_sqlalchemy_tools.SelectStatement[
            saritasa_sqlalchemy_tools.BaseModelT
        ],
        saritasa_sqlalchemy_tools.Annotation,
        saritasa_sqlalchemy_tools.WhereFilter,
        saritasa_sqlalchemy_tools.OrderingClause,
        permissions.UserT,
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        views.CreateSchema,
        views.DetailSchema,
        permissions.UserT,
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """Create mixin for sqlalchemy."""


class UpdateMixin(
    views.UpdateMixin[
        views.UpdateSchema,
        views.DetailSchema,
        saritasa_sqlalchemy_tools.LazyLoaded,
        saritasa_sqlalchemy_tools.SelectStatement[
            saritasa_sqlalchemy_tools.BaseModelT
        ],
        saritasa_sqlalchemy_tools.Annotation,
        saritasa_sqlalchemy_tools.WhereFilter,
        saritasa_sqlalchemy_tools.OrderingClause,
        permissions.UserT,
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        views.UpdateSchema,
        views.DetailSchema,
        permissions.UserT,
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """Update mixin for sqlalchemy."""


class DeleteMixin(
    views.DeleteMixin[
        saritasa_sqlalchemy_tools.LazyLoaded,
        saritasa_sqlalchemy_tools.SelectStatement[
            saritasa_sqlalchemy_tools.BaseModelT
        ],
        saritasa_sqlalchemy_tools.Annotation,
        saritasa_sqlalchemy_tools.WhereFilter,
        saritasa_sqlalchemy_tools.OrderingClause,
        permissions.UserT,
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        permissions.UserT,
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
):
    """Update mixin for sqlalchemy."""
