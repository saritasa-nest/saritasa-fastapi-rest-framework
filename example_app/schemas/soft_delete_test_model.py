import saritasa_sqlalchemy_tools

from .. import models


class SoftDeleteTestModelCreateDetailAutoSchema(
    saritasa_sqlalchemy_tools.ModelAutoSchema,
):
    """Detail schema for create."""

    class Meta:
        model = models.SoftDeleteTestModel
        fields = (
            "id",
            "created",
        )


SoftDeleteTestCreateModelDetail = (
    SoftDeleteTestModelCreateDetailAutoSchema.get_schema()
)


class SoftDeleteTestModelUpdateDetailAutoSchema(
    saritasa_sqlalchemy_tools.ModelAutoSchema,
):
    """Detail schema for update."""

    class Meta:
        model = models.SoftDeleteTestModel
        fields = (
            "id",
            "modified",
        )


SoftDeleteTestUpdateModelDetail = (
    SoftDeleteTestModelUpdateDetailAutoSchema.get_schema()
)


class SoftDeleteTestModelCreateUpdateRequestAutoSchema(
    saritasa_sqlalchemy_tools.ModelAutoSchema,
):
    """Detail schema."""

    class Meta:
        model = models.SoftDeleteTestModel
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
            "json_field",
            "json_field_nullable",
            "date_range",
            "date_range_nullable",
        )


SoftDeleteTestModelCreateUpdateRequest = (
    SoftDeleteTestModelCreateUpdateRequestAutoSchema.get_schema()
)
