import fastapi

import fastapi_rest_framework

from .. import repositories, schemas, security
from . import core


class Context(fastapi_rest_framework.Context):
    """Representation of context for soft_delete_test_models API."""


class SoftDeleteTestModelAPIView(
    core.DeleteMixin[
        repositories.SoftDeleteTestModelRepository,
        repositories.SoftDeleteTestModelRepository.model,
    ],
    core.UpdateMixin[
        schemas.TestModelUpdateRequest,
        schemas.TestModelDetail,
        repositories.SoftDeleteTestModelRepository,
        repositories.SoftDeleteTestModelRepository.model,
    ],
    core.CreateMixin[
        schemas.TestModelCreateRequest,
        schemas.TestModelDetail,
        repositories.SoftDeleteTestModelRepository,
        repositories.SoftDeleteTestModelRepository.model,
    ],
    core.BaseView[
        repositories.SoftDeleteTestModelRepository,
        repositories.SoftDeleteTestModelRepository.model,
    ],
):
    """SoftDeleteTestModel API."""

    router = fastapi.APIRouter(
        prefix="/soft-delete-test-models",
        tags=["SoftDeleteTestModel"],
    )
    repository_class = repositories.SoftDeleteTestModelRepository
    model = repository_class.model
    base_permissions = (security.AuthRequiredPermission[model](),)
    permission_map = {  # noqa: RUF012
        "delete": (security.AllowPermission[model](),),
    }
    create_schema = schemas.SoftDeleteTestModelCreateUpdateRequest
    create_detail_schema = schemas.SoftDeleteTestCreateModelDetail
    update_schema = schemas.SoftDeleteTestModelCreateUpdateRequest
    update_detail_schema = schemas.SoftDeleteTestUpdateModelDetail
    context = Context
