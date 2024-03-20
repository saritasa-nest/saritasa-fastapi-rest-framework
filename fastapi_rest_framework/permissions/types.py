import typing

UserT = typing.TypeVar("UserT", bound=typing.Any)
RequestData: typing.TypeAlias = dict[str, typing.Any] | None
