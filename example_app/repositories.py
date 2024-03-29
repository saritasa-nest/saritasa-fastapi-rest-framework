import typing

import sqlalchemy

import fastapi_rest_framework

from . import models


class RelatedModelRepository(
    fastapi_rest_framework.sqlalchemy.SqlAlchemyRepository[
        models.RelatedModel
    ],
):
    """Repository for `RelatedModel` model."""

    model: typing.TypeAlias = models.RelatedModel
    default_exclude_bulk_create_fields = (
        "created",
        "modified",
        "id",
    )
    default_exclude_bulk_update_fields = (
        "created",
        "modified",
    )


class TestModelRepository(
    fastapi_rest_framework.sqlalchemy.SqlAlchemyRepository[models.TestModel],
):
    """Repository for `TestModel` model."""

    model: typing.TypeAlias = models.TestModel
    default_exclude_bulk_create_fields = (
        "created",
        "modified",
        "id",
    )
    default_exclude_bulk_update_fields = (
        "created",
        "modified",
    )

    @classmethod
    def get_related_models_count_query(cls) -> sqlalchemy.ScalarSelect[int]:
        """Get query for get_related_models_count_query."""
        return (
            sqlalchemy.select(sqlalchemy.func.count(models.RelatedModel.id))
            .where(
                models.RelatedModel.test_model_id == models.TestModel.id,
            )
            .correlate_except(models.RelatedModel)
            .scalar_subquery()
        )


class SoftDeleteTestModelRepository(
    fastapi_rest_framework.sqlalchemy.SqlAlchemySoftDeleteRepository[
        models.SoftDeleteTestModel
    ],
):
    """Repository for `SoftDeleteTestModel` model."""

    model: typing.TypeAlias = models.SoftDeleteTestModel
    default_exclude_bulk_create_fields = (
        "created",
        "modified",
        "id",
    )
    default_exclude_bulk_update_fields = (
        "created",
        "modified",
    )


class M2MModelRepository(
    fastapi_rest_framework.sqlalchemy.SqlAlchemyRepository[models.M2MModel],
):
    """Repository for `M2MModel` model."""

    model: typing.TypeAlias = models.M2MModel
    default_exclude_bulk_create_fields = (
        "created",
        "modified",
        "id",
    )
    default_exclude_bulk_update_fields = (
        "created",
        "modified",
    )
