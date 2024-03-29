import pydantic
import saritasa_sqlalchemy_tools

from .. import models


class RelatedModelTestModelAutoSchema(
    saritasa_sqlalchemy_tools.ModelAutoSchema,
):
    """Schema for related model in test model."""

    class Meta:
        model = models.RelatedModel
        fields = (
            "id",
            "created",
            "modified",
        )


class TestModelListAutoSchema(saritasa_sqlalchemy_tools.ModelAutoSchema):
    """List schema."""

    class Meta:
        model = models.TestModel
        model_config = pydantic.ConfigDict(
            from_attributes=True,
        )
        fields = (
            "text_unique",
            "id",
            "created",
            "modified",
            "text",
            "text_nullable",
            "text_enum",
            "text_enum_nullable",
            "timezone",
            "number",
            "number_nullable",
            "small_number",
            "small_number_nullable",
            "decimal_number",
            "decimal_number_nullable",
            "boolean",
            "boolean_nullable",
            "text_list",
            "text_list_nullable",
            "date_time",
            "date_time_nullable",
            "date",
            "date_nullable",
            "timedelta",
            "timedelta_nullable",
            "related_model_id",
            "related_model_id_nullable",
            "custom_property",
            "custom_property_nullable",
            "json_field",
            "json_field_nullable",
            (
                "related_models_count",
                int,
            ),
            (
                "related_model",
                RelatedModelTestModelAutoSchema,
            ),
            (
                "related_models",
                RelatedModelTestModelAutoSchema,
            ),
        )


TestModelList = TestModelListAutoSchema.get_schema()


class TestModelDetailAutoSchema(saritasa_sqlalchemy_tools.ModelAutoSchema):
    """Detail schema."""

    class Meta:
        model = models.TestModel
        fields = (
            "text_unique",
            "id",
            "created",
            "modified",
            "text",
            "text_nullable",
            "text_enum",
            "text_enum_nullable",
            "timezone",
            "number",
            "number_nullable",
            "small_number",
            "small_number_nullable",
            "decimal_number",
            "decimal_number_nullable",
            "boolean",
            "boolean_nullable",
            "text_list",
            "text_list_nullable",
            "date_time",
            "date_time_nullable",
            "date",
            "date_nullable",
            "timedelta",
            "timedelta_nullable",
            "related_model_id",
            "related_model_id_nullable",
            "custom_property",
            "custom_property_nullable",
            "json_field",
            "json_field_nullable",
            (
                "related_models_count",
                int,
            ),
            (
                "related_models_count_query",
                int,
            ),
            (
                "related_model",
                RelatedModelTestModelAutoSchema,
            ),
            (
                "related_model_nullable",
                RelatedModelTestModelAutoSchema,
            ),
            (
                "related_models",
                RelatedModelTestModelAutoSchema,
            ),
            (
                "m2m_related_models",
                RelatedModelTestModelAutoSchema,
            ),
        )


TestModelDetail = TestModelDetailAutoSchema.get_schema()


class TestModelCreateRequestAutoSchema(
    saritasa_sqlalchemy_tools.ModelAutoSchema,
):
    """Detail schema."""

    class Meta:
        model = models.TestModel
        fields = (
            "text_unique",
            "text",
            "text_nullable",
            "text_enum",
            "text_enum_nullable",
            "timezone",
            "number",
            "number_nullable",
            "small_number",
            "small_number_nullable",
            "decimal_number",
            "decimal_number_nullable",
            "boolean",
            "boolean_nullable",
            "text_list",
            "text_list_nullable",
            "date_time",
            "date_time_nullable",
            "date",
            "date_nullable",
            "timedelta",
            "timedelta_nullable",
            "related_model_id",
            "related_model_id_nullable",
            "json_field",
            "json_field_nullable",
            ("m2m_related_models_ids", list[int]),
        )


TestModelCreateRequest = TestModelCreateRequestAutoSchema.get_schema()


class TestModelBulkCreateRequestAutoSchema(
    saritasa_sqlalchemy_tools.ModelAutoSchema,
):
    """Detail schema."""

    class Meta:
        model = models.TestModel
        fields = (
            "text_unique",
            "text",
            "text_nullable",
            "text_enum",
            "text_enum_nullable",
            "timezone",
            "number",
            "number_nullable",
            "small_number",
            "small_number_nullable",
            "decimal_number",
            "decimal_number_nullable",
            "boolean",
            "boolean_nullable",
            "text_list",
            "text_list_nullable",
            "date_time",
            "date_time_nullable",
            "date",
            "date_nullable",
            "timedelta",
            "timedelta_nullable",
            "related_model_id",
            "related_model_id_nullable",
            "json_field",
            "json_field_nullable",
        )


TestModelBulkCreateRequest = TestModelBulkCreateRequestAutoSchema.get_schema()


class TestModelUpdateRequestAutoSchema(
    saritasa_sqlalchemy_tools.ModelAutoSchema,
):
    """Detail schema."""

    class Meta:
        model = models.TestModel
        fields = (
            "text_unique",
            "text",
            "text_nullable",
            "text_enum",
            "text_enum_nullable",
            "timezone",
            "number",
            "number_nullable",
            "small_number",
            "small_number_nullable",
            "decimal_number",
            "decimal_number_nullable",
            "boolean",
            "boolean_nullable",
            "text_list",
            "text_list_nullable",
            "date_time",
            "date_time_nullable",
            "date",
            "date_nullable",
            "timedelta",
            "timedelta_nullable",
            "related_model_id",
            "related_model_id_nullable",
            "json_field",
            "json_field_nullable",
            ("m2m_related_models_ids", list[int]),
        )


TestModelUpdateRequest = TestModelUpdateRequestAutoSchema.get_schema()
