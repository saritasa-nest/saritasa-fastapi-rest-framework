import collections.abc
import typing

import httpx
import starlette.datastructures

from .. import permissions

AuthApiClientFactory: typing.TypeAlias = collections.abc.Callable[
    [permissions.UserT | None],
    httpx.AsyncClient,
]
LazyUrl: typing.TypeAlias = collections.abc.Callable[
    ...,
    starlette.datastructures.URLPath,
]
