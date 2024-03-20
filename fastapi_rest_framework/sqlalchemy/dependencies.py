import collections.abc
import typing

import fastapi
import saritasa_sqlalchemy_tools


def get_repository(
    repository_class: type[
        saritasa_sqlalchemy_tools.BaseRepository[
            saritasa_sqlalchemy_tools.BaseModelT
        ]
    ],
    session_dependency: type[saritasa_sqlalchemy_tools.Session],
) -> collections.abc.Callable[
    ...,
    saritasa_sqlalchemy_tools.BaseRepository[
        saritasa_sqlalchemy_tools.BaseModelT
    ],
]:
    """Get dependency injection for db repository."""

    def _get_repository(
        session: typing.Annotated[
            saritasa_sqlalchemy_tools.Session,
            fastapi.Depends(session_dependency),
        ],
    ) -> saritasa_sqlalchemy_tools.BaseRepository[
        saritasa_sqlalchemy_tools.BaseModelT
    ]:
        return repository_class(db_session=session)

    return _get_repository
