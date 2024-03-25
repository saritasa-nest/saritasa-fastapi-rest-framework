import typing

ApiDataType: typing.TypeAlias = dict[str, typing.Any]
# Location of error. For example this input data has some errors
# {
#   "name": null <- error,
#   "list": [
#      "test",
#      null <- error
#    ]
# }
# Then for this error will have loc `body.name` and second will have
# `body.list.1`
LOCType: typing.TypeAlias = tuple[str | int, ...]
AnyGenericInput = typing.TypeVar("AnyGenericInput", bound=typing.Any)
AnyGenericOutput = typing.TypeVar("AnyGenericOutput", bound=typing.Any)
