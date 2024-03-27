import typing

import saritasa_sqlalchemy_tools

from .. import repositories


class SqlAlchemyRepository(  # type: ignore[misc]
    saritasa_sqlalchemy_tools.BaseRepository[
        saritasa_sqlalchemy_tools.BaseModelT
    ],
    repositories.ApiRepositoryProtocol[
        saritasa_sqlalchemy_tools.BaseModelT,
        saritasa_sqlalchemy_tools.SelectStatement[
            saritasa_sqlalchemy_tools.BaseModelT
        ],
        saritasa_sqlalchemy_tools.WhereFilter,
        saritasa_sqlalchemy_tools.OrderingClause,
        saritasa_sqlalchemy_tools.Annotation,
        saritasa_sqlalchemy_tools.LazyLoaded,
    ],
    typing.Generic[saritasa_sqlalchemy_tools.BaseModelT],
):
    """Repository for sqlalchemy."""


SqlAlchemyRepositoryT = typing.TypeVar(
    "SqlAlchemyRepositoryT",
    bound=SqlAlchemyRepository[typing.Any],
)


class SqlAlchemySoftDeleteRepository(  # type: ignore[misc]
    saritasa_sqlalchemy_tools.BaseSoftDeleteRepository[
        saritasa_sqlalchemy_tools.BaseSoftDeleteModelT
    ],
    repositories.ApiRepositoryProtocol[
        saritasa_sqlalchemy_tools.BaseSoftDeleteModelT,
        saritasa_sqlalchemy_tools.SelectStatement[
            saritasa_sqlalchemy_tools.BaseSoftDeleteModelT
        ],
        saritasa_sqlalchemy_tools.WhereFilter,
        saritasa_sqlalchemy_tools.OrderingClause,
        saritasa_sqlalchemy_tools.Annotation,
        saritasa_sqlalchemy_tools.LazyLoaded,
    ],
    typing.Generic[saritasa_sqlalchemy_tools.BaseSoftDeleteModelT],
):
    """SoftDeleteRepository for sqlalchemy."""
