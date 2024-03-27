import collections.abc
import typing

import httpx

import example_app

UserData: typing.TypeAlias = example_app.security.UserJWTData
AuthApiClientFactory: typing.TypeAlias = collections.abc.Callable[
    [UserData | None],
    httpx.AsyncClient,
]
