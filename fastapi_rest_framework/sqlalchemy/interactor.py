import typing

import saritasa_sqlalchemy_tools

from .. import interactors, permissions
from . import repositories


class SqlAlchemyInteractor(
    interactors.ApiDataInteractor[
        permissions.UserT,
        saritasa_sqlalchemy_tools.SelectStatement[
            saritasa_sqlalchemy_tools.BaseModelT
        ],
        repositories.SqlAlchemyRepositoryT,
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[
        permissions.UserT,
        saritasa_sqlalchemy_tools.BaseModelT,
        repositories.SqlAlchemyRepositoryT,
    ],
):
    """Interactor for sqlalchemy."""


class SqlAlchemyInteractorHooksMixin(
    interactors.BaseHooksMixin[saritasa_sqlalchemy_tools.BaseModelT],
):
    """Hooks for sqlalchemy."""
