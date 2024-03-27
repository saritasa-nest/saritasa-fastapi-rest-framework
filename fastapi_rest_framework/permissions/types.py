import typing

import pydantic

UserT = typing.TypeVar("UserT", bound=pydantic.BaseModel)
RequestData: typing.TypeAlias = dict[str, typing.Any] | None
