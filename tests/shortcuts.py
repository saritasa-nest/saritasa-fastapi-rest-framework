import typing

import example_app
import fastapi_rest_framework

UserData: typing.TypeAlias = example_app.security.UserJWTData
AuthApiClientFactory: typing.TypeAlias = (
    fastapi_rest_framework.testing.AuthApiClientFactory[UserData]
)
