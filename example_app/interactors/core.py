import typing

import saritasa_sqlalchemy_tools

import fastapi_rest_framework

from .. import security


class Interactor(
    fastapi_rest_framework.sqlalchemy.SqlAlchemyInteractor[
        security.UserJWTData,
        saritasa_sqlalchemy_tools.BaseModelT,
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
    ],
    typing.Generic[
        saritasa_sqlalchemy_tools.BaseModelT,
        fastapi_rest_framework.sqlalchemy.SqlAlchemyRepositoryT,
    ],
):
    """Base interactor."""


class InteractorHooksMixin(
    fastapi_rest_framework.sqlalchemy.SqlAlchemyInteractorHooksMixin[
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[saritasa_sqlalchemy_tools.BaseModelT,],
):
    """Base hooks mixin."""


class S3InteractorMixin(
    fastapi_rest_framework.s3.S3InteractorMixin[
        saritasa_sqlalchemy_tools.BaseModelT,
    ],
    typing.Generic[saritasa_sqlalchemy_tools.BaseModelT,],
):
    """S3 mixin."""

    upload_folder = "upload"
