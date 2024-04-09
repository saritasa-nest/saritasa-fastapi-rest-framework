import http

import fastapi
import pydantic
import saritasa_sqlalchemy_tools
import sqlalchemy

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
    text__in: list[str] = pydantic.Field(fastapi.Query(()))
    number__gte: int | None = pydantic.Field(fastapi.Query(None))
    m2m_related_model_id__in: list[int] = pydantic.Field(fastapi.Query(()))
    is_boolean_condition_true: bool = pydantic.Field(fastapi.Query(False))

    def transform_is_boolean_condition_true(
        self,
        user: security.UserJWTData,
        model: type[repositories.TestModelRepository.model],
        value: bool,
        context: fastapi_rest_framework.ContextType,
    ) -> saritasa_sqlalchemy_tools.WhereFilter:
        """Transform is_boolean filter."""
        if value:
            return model.boolean.is_(True)
        return sqlalchemy.or_(
            model.boolean.is_(True),
            model.boolean.is_(False),
        )


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
        prefix="/test-models",
        tags=["TestModels"],
    )
    repository_class = repositories.TestModelRepository
    model = repository_class.model
    joined_load_map = {  # noqa: RUF012
        "default": (),
    }
    base_permissions = (security.AuthRequiredPermission[model](),)
    permission_map = {  # noqa: RUF012
        "default": (security.AllowPermission[model](),),
        "action": (security.AllowPermission[model](),),
    }
    validators_map = {  # noqa: RUF012
        "default": validators.TestModelValidator,
        "action": validators.ListTestModelValidator,
    }
    annotations_map = {  # noqa: RUF012
        "default": (
            repositories.TestModelRepository.model.related_models_count,
        ),
        "detail": (
            repositories.TestModelRepository.model.related_models_count,
            (
                repositories.TestModelRepository.model.related_models_count_query,
                repositories.TestModelRepository.get_related_models_count_query(),
            ),
        ),
        "create": (
            repositories.TestModelRepository.model.related_models_count,
            (
                repositories.TestModelRepository.model.related_models_count_query,
                repositories.TestModelRepository.get_related_models_count_query(),
            ),
        ),
        "update": (
            repositories.TestModelRepository.model.related_models_count,
            (
                repositories.TestModelRepository.model.related_models_count_query,
                repositories.TestModelRepository.get_related_models_count_query(),
            ),
        ),
        "delete": (),
    }
    select_in_load_map = {  # noqa: RUF012
        "default": (repositories.TestModelRepository.model.related_model,),
        "detail": (
            repositories.TestModelRepository.model.related_model,
            repositories.TestModelRepository.model.related_model_nullable,
        ),
        "create": (
            repositories.TestModelRepository.model.related_model,
            repositories.TestModelRepository.model.related_model_nullable,
        ),
        "update": (
            repositories.TestModelRepository.model.related_model,
            repositories.TestModelRepository.model.related_model_nullable,
        ),
        "delete": (),
    }
    joined_load_map = {  # noqa: RUF012
        "default": (repositories.TestModelRepository.model.related_models,),
        "detail": (
            repositories.TestModelRepository.model.related_models,
            repositories.TestModelRepository.model.m2m_related_models,
        ),
        "create": (
            repositories.TestModelRepository.model.related_models,
            repositories.TestModelRepository.model.m2m_related_models,
        ),
        "update": (
            repositories.TestModelRepository.model.related_models,
            repositories.TestModelRepository.model.m2m_related_models,
        ),
        "delete": (),
    }
    interactor = interactors.TestModelInteractor
    detail_schema = schemas.TestModelDetail
    list_schema = schemas.TestModelList
    filter = Filters
    ordering_fields = ("id",)
    create_schema = schemas.TestModelCreateRequest
    update_schema = schemas.TestModelUpdateRequest
    context = Context

    @fastapi_rest_framework.action(paginated=True)
    async def paginated_action(
        self,
        user: security.UserJWTData,
        repository: repositories.TestModelRepository,
        context: Context,
        pagination_params: fastapi_rest_framework.PaginationParams[Filters],
        annotations: saritasa_sqlalchemy_tools.AnnotationSequence,
        joined_load: saritasa_sqlalchemy_tools.LazyLoadedSequence,
        select_in_load: saritasa_sqlalchemy_tools.LazyLoadedSequence,
        **kwargs,
    ) -> fastapi_rest_framework.PaginatedResult[schemas.TestModelList]:
        """Perform paginated action."""
        return await self.perform_list(
            user=user,
            repository=repository,
            context=context,
            list_schema=schemas.TestModelList,
            annotations=(*annotations,),
            pagination_params=pagination_params,
            joined_load=joined_load,
            select_in_load=select_in_load,
        )

    @fastapi_rest_framework.action(
        method=http.HTTPMethod.POST,
        status_code=http.HTTPStatus.NO_CONTENT,
    )
    async def action(
        self,
        user: security.UserJWTData,
        repository: repositories.TestModelRepository,
        objects: list[schemas.TestModelBulkCreateRequest],
        validator: type[validators.ListTestModelValidator],
        interactor: type[interactors.TestModelInteractor],
        context: Context,
        **kwargs,
    ) -> None:
        """Recreate all instances."""
        data = await validator(repository=repository)(
            value=list(map(dict, objects)),
            context=dict(context),
        )
        if data is None:
            return
        await repository.delete_batch()
        await interactor(
            repository=repository,
            user=user,
        ).create_batch(
            data=data,
            context=dict(context),
        )

    @fastapi_rest_framework.action(
        method=http.HTTPMethod.PUT,
        detail=True,
        status_code=http.HTTPStatus.NO_CONTENT,
    )
    async def action_detail(
        self,
        user: security.UserJWTData,
        repository: repositories.TestModelRepository,
        instance: repositories.TestModelRepository.model,
        interactor: type[interactors.TestModelInteractor],
        context: Context,
        **kwargs,
    ) -> None:
        """Perform action."""
        await interactor(
            repository=repository,
            user=user,
            instance=instance,
        ).save(
            data={
                "text_unique": "text_unique_action_detail",
            },
            context=dict(context),
        )
