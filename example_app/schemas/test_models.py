import pydantic
import saritasa_sqlalchemy_tools

from .. import models


class TestModelListAutoSchema(saritasa_sqlalchemy_tools.ModelAutoSchema):
    """List schema."""

    class Meta:
        model = models.TestModel
        model_config = pydantic.ConfigDict(
            from_attributes=True,
        )
        fields = (
            "id",
            "created",
            "modified",
            "text",
            "text_nullable",
            "text_enum",
            "text_enum_nullable",
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
        )


TestModelList = TestModelListAutoSchema.get_schema()


class TestModelDetailAutoSchema(saritasa_sqlalchemy_tools.ModelAutoSchema):
    """Detail schema."""

    class Meta:
        model = models.TestModel
        model_config = pydantic.ConfigDict(
            from_attributes=True,
        )
        fields = (
            "id",
            "created",
            "modified",
            "text",
            "text_nullable",
            "text_enum",
            "text_enum_nullable",
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
        )


TestModelDetail = TestModelDetailAutoSchema.get_schema()


class TestModelCreateRequestAutoSchema(
    saritasa_sqlalchemy_tools.ModelAutoSchema,
):
    """Detail schema."""

    class Meta:
        model = models.TestModel
        model_config = pydantic.ConfigDict(
            from_attributes=True,
        )
        fields = (
            "text",
            "text_nullable",
            "text_enum",
            "text_enum_nullable",
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


TestModelCreateRequest = TestModelCreateRequestAutoSchema.get_schema()


class TestModelUpdateRequestAutoSchema(
    saritasa_sqlalchemy_tools.ModelAutoSchema,
):
    """Detail schema."""

    class Meta:
        model = models.TestModel
        model_config = pydantic.ConfigDict(
            from_attributes=True,
        )
        fields = (
            "text",
            "text_nullable",
            "text_enum",
            "text_enum_nullable",
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


TestModelUpdateRequest = TestModelUpdateRequestAutoSchema.get_schema()
