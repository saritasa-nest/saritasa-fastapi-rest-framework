import typing

import example_app
import fastapi_rest_framework

UserData: typing.TypeAlias = example_app.security.UserJWTData
AuthApiClientFactory: typing.TypeAlias = (
    fastapi_rest_framework.testing.AuthApiClientFactory[UserData]
)
JWTAuthenticationType: typing.TypeAlias = example_app.security.JWTAuthClass
JWTAuthentication: JWTAuthenticationType = example_app.security.JWTAuth
