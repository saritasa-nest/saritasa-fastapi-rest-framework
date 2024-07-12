import typing

import saritasa_sqlalchemy_tools

from .. import common_types, interactors, metrics, permissions, validators
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

    @metrics.tracker
    def _prepare_data_for_instance(
        self,
        data: validators.ApiDataType,
        context: common_types.ContextType,
    ) -> validators.ApiDataType:
        """Prepare data for instance init or update."""
        prepared_data: validators.ApiDataType = {}
        for key, value in data.items():
            if to_db := getattr(value, "to_db", None):
                value = to_db()
            prepared_data[key] = value
        return prepared_data


class SqlAlchemyInteractorHooksMixin(
    interactors.BaseHooksMixin[saritasa_sqlalchemy_tools.BaseModelT],
):
    """Hooks for sqlalchemy."""
