import fastapi_rest_framework

from .. import repositories


class TextListValidator(
    fastapi_rest_framework.BaseValidator[str, str],
):
    """Validate value in text_list."""

    async def _validate(
        self,
        value: str | None,
        loc: fastapi_rest_framework.LOCType,
        context: fastapi_rest_framework.ContextType,
    ) -> str | None:
        """Perform validation."""
        if not value:
            return value
        if value == "invalid":
            raise fastapi_rest_framework.ValidationError(
                error_type=fastapi_rest_framework.ValidationErrorType.invalid,
                error_message="Value is invalid",
            )
        return value


class TestModelValidator(
    fastapi_rest_framework.BaseModelValidator[
        repositories.TestModelRepository,
        repositories.TestModelRepository.model,
    ],
):
    """Validate test model data."""

    def _get_unique_constraints(
        self,
    ) -> list[fastapi_rest_framework.UniqueConstraintType]:
        return [
            (
                "text",
                "text_nullable",
            ),
        ]

    def _get_validation_map(
        self,
        value: fastapi_rest_framework.ApiDataType,
        context: fastapi_rest_framework.ContextType,
    ) -> fastapi_rest_framework.ValidationMapType:
        return {
            "text_unique": (
                fastapi_rest_framework.UniqueByFieldValidator(
                    field="text_unique",
                    repository=self.repository,
                    human_name="Text unique",
                    instance=self.instance,
                ),
            ),
            "text_nullable": (
                fastapi_rest_framework.RegexValidator(
                    pattern=r"([A-Z])\w+",
                    human_error="Regex validation failed",
                ),
                fastapi_rest_framework.NotEqualToValues(
                    values=["NotEqualToValues"],
                ),
            ),
            "timezone": (fastapi_rest_framework.TimeZoneValidator(),),
            "date_time": (fastapi_rest_framework.DatetimeValidator(),),
            "date_time_nullable": (
                fastapi_rest_framework.DatetimeValidator(),
            ),
            "text_list": (
                fastapi_rest_framework.BaseListValidator(
                    instance_validator=TextListValidator(),
                ),
            ),
            "text_list_nullable": (
                fastapi_rest_framework.BaseListValidator(
                    instance_validator=TextListValidator(),
                ),
            ),
            "related_model_id": (
                fastapi_rest_framework.ObjectPKValidator(
                    human_name="related model",
                    repository=self.repository.init_other(
                        repositories.RelatedModelRepository,
                    ),
                ),
            ),
            "related_model_id_nullable": (
                fastapi_rest_framework.ObjectPKValidator(
                    human_name="related model",
                    repository=self.repository.init_other(
                        repositories.RelatedModelRepository,
                    ),
                ),
            ),
            "m2m_related_models_ids": (
                fastapi_rest_framework.ObjectPKValidator(
                    human_name="related models",
                    repository=self.repository.init_other(
                        repositories.RelatedModelRepository,
                    ),
                ),
            ),
        }


class ListTestModelValidator(
    fastapi_rest_framework.BaseModelListValidator[
        repositories.TestModelRepository,
        repositories.TestModelRepository.model,
    ],
):
    """Validate list of user timezones."""

    def __init__(
        self,
        repository: repositories.TestModelRepository,
    ) -> None:
        super().__init__(
            instance_validator=TestModelValidator,
            repository=repository,
        )
