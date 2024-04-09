import typing

import pydantic

from .. import interactors, permissions, repositories, validators

DetailSchema = typing.TypeVar(
    "DetailSchema",
    bound=pydantic.BaseModel,
)
ListSchema = typing.TypeVar(
    "ListSchema",
    bound=pydantic.BaseModel,
)
CreateSchema = typing.TypeVar(
    "CreateSchema",
    bound=pydantic.BaseModel,
)
UpdateSchema = typing.TypeVar(
    "UpdateSchema",
    bound=pydantic.BaseModel,
)

ResponsesMap: typing.TypeAlias = dict[int | str, dict[str, typing.Any]]
ActionResponsesMap: typing.TypeAlias = dict[str, ResponsesMap]
ActionValidatorType: typing.TypeAlias = type[
    validators.BaseModelValidator[
        repositories.ApiRepositoryProtocolT,
        repositories.APIModelT,
    ]
    | validators.BaseModelListValidator[
        repositories.ApiRepositoryProtocolT,
        repositories.APIModelT,
    ]
]
ActionInteractorType: typing.TypeAlias = type[
    interactors.ApiDataInteractor[
        permissions.UserT,
        repositories.SelectStatementT,
        repositories.ApiRepositoryProtocolT,
        repositories.APIModelT,
    ]
]


class Context(pydantic.BaseModel):
    """Base representation of context.

    Example:
    -------
    class Context(core.Context):
        some_dep: typing.Annotated[Type, fastapi.Depends(Dep)]

    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    )
