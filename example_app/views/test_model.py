import fastapi
import pydantic

import fastapi_rest_framework

from .. import interactors, repositories, schemas, security, validators
from . import core


class Context(fastapi_rest_framework.Context):
    """Representation of context for test_models API."""


class Filters(core.Filters[repositories.TestModelRepository.model]):
    """Define filters for test_models model."""

    _model = repositories.TestModelRepository.model
    _search_fields = (
        "id",
        "text",
    )

    search: str = pydantic.Field(fastapi.Query(""))


class TestModelAPIView(
    core.DeleteMixin[
        repositories.TestModelRepository,
        repositories.TestModelRepository.model,
    ],
    core.UpdateMixin[
        schemas.TestModelUpdateRequest,
        schemas.TestModelDetail,
        repositories.TestModelRepository,
        repositories.TestModelRepository.model,
    ],
    core.CreateMixin[
        schemas.TestModelCreateRequest,
        schemas.TestModelDetail,
        repositories.TestModelRepository,
        repositories.TestModelRepository.model,
    ],
    core.DetailMixin[
        schemas.TestModelDetail,
        repositories.TestModelRepository,
        repositories.TestModelRepository.model,
    ],
    core.ListMixin[
        schemas.TestModelList,
        Filters,
        repositories.TestModelRepository,
        repositories.TestModelRepository.model,
    ],
    core.BaseView[
        repositories.TestModelRepository,
        repositories.TestModelRepository.model,
    ],
):
    """TestModel API."""

    router = fastapi.APIRouter(
        prefix="/test_models",
        tags=["TestModels"],
    )
    repository_class = repositories.TestModelRepository
    model = repository_class.model
    joined_load_map = {  # noqa: RUF012
        "default": (),
    }
    permission_map = {  # noqa: RUF012
        "default": (security.AuthRequiredPermission[model](),),
    }
    validators_map = {  # noqa: RUF012
        "default": validators.TestModelValidator,
    }
    data_interactor = interactors.TestModelInteractor
    detail_schema = schemas.TestModelDetail
    list_schema = schemas.TestModelList
    filter = Filters
    ordering_fields = ("id",)
    create_schema = schemas.TestModelCreateRequest
    update_schema = schemas.TestModelUpdateRequest
    context = Context
