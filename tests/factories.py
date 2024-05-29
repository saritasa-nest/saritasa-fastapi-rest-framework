import datetime
import typing

import botocore.credentials
import factory
import factory.fuzzy
import saritasa_s3_tools
import saritasa_sqlalchemy_tools

import example_app

S3ImageFactory = saritasa_s3_tools.factory.S3ImageFileField(
    s3_config="files",
    s3_region=example_app.config.aws_region,
    bucket=example_app.config.s3_bucket,
    access_key_getter=lambda: botocore.credentials.Credentials(
        access_key=example_app.config.aws_access_key,
        secret_key=example_app.config.aws_secret_key,
    ),
    s3_endpoint_url_getter=lambda: example_app.config.aws_endpoint,
)


class UserJWTDataFactory(factory.Factory):
    """Factory to generate test UserJWTData instance."""

    id = factory.Faker(
        "pyint",
        min_value=1,
    )
    allow = True
    iat = datetime.datetime.now(datetime.UTC)
    exp = iat + datetime.timedelta(days=100)

    class Meta:
        model = example_app.security.UserJWTData


class TestModelFactory(
    saritasa_sqlalchemy_tools.AsyncSQLAlchemyModelFactory[
        example_app.repositories.TestModelRepository.model,
        example_app.repositories.TestModelRepository,
    ],
):
    """Factory to generate TestModel."""

    text_unique = factory.Faker(
        "pystr",
        min_chars=400,
        max_chars=500,
    )
    text = factory.Faker(
        "pystr",
        min_chars=1,
        max_chars=30,
    )
    text_enum = factory.fuzzy.FuzzyChoice(
        example_app.models.TestModel.TextEnum,
    )
    timezone = factory.Faker("timezone")
    number = factory.Faker("pyint")
    small_number = factory.Faker("pyint")
    decimal_number = factory.Faker(
        "pydecimal",
        positive=True,
        left_digits=5,
        right_digits=0,
    )
    boolean = factory.Faker("pybool")
    text_list = factory.List(
        [
            factory.Faker(
                "pystr",
                min_chars=1,
                max_chars=30,
            )
            for _ in range(3)
        ],
    )
    date_time = factory.Faker("date_time")
    date = factory.Faker("date_between")
    timedelta = factory.Faker("time_delta")
    json_field = factory.Faker("pydict", allowed_types=[str, int, float])
    date_range = saritasa_sqlalchemy_tools.DateRangeFactory()
    file = S3ImageFactory
    files = factory.List([S3ImageFactory for _ in range(2)])

    class Meta:
        model = example_app.models.TestModel
        repository = example_app.repositories.TestModelRepository
        sub_factories: typing.ClassVar = {
            "related_model": "tests.factories.RelatedModelFactory",
            "related_models": ("tests.factories.RelatedModelFactory", 5),
        }


class SoftDeleteTestModelFactory(
    saritasa_sqlalchemy_tools.AsyncSQLAlchemyModelFactory[
        example_app.repositories.SoftDeleteTestModelRepository.model,
        example_app.repositories.SoftDeleteTestModelRepository,
    ],
):
    """Factory to generate SoftDeleteTestModel."""

    text_unique = factory.Faker(
        "pystr",
        min_chars=400,
        max_chars=500,
    )
    text = factory.Faker(
        "pystr",
        min_chars=200,
        max_chars=250,
    )
    text_enum = factory.fuzzy.FuzzyChoice(
        example_app.models.TestModel.TextEnum,
    )
    timezone = factory.Faker("timezone")
    number = factory.Faker("pyint")
    small_number = factory.Faker("pyint")
    decimal_number = factory.Faker(
        "pydecimal",
        positive=True,
        left_digits=5,
        right_digits=0,
    )
    boolean = factory.Faker("pybool")
    text_list = factory.List(
        [
            factory.Faker(
                "pystr",
                min_chars=1,
                max_chars=30,
            )
            for _ in range(3)
        ],
    )
    date_time = factory.Faker("date_time")
    date = factory.Faker("date_between")
    timedelta = factory.Faker("time_delta")
    json_field = factory.Faker("pydict", allowed_types=[str, int, float])
    date_range = saritasa_sqlalchemy_tools.DateRangeFactory()
    file = S3ImageFactory
    files = factory.List([S3ImageFactory for _ in range(2)])

    class Meta:
        model = example_app.models.SoftDeleteTestModel
        repository = example_app.repositories.SoftDeleteTestModelRepository


class RelatedModelFactory(
    saritasa_sqlalchemy_tools.AsyncSQLAlchemyModelFactory[
        example_app.repositories.RelatedModelRepository.model,
        example_app.repositories.RelatedModelRepository,
    ],
):
    """Factory to generate RelatedModel."""

    text = factory.Faker(
        "pystr",
        min_chars=1,
        max_chars=30,
    )
    number = factory.Faker("pyint")

    class Meta:
        model = example_app.models.RelatedModel
        repository = example_app.repositories.RelatedModelRepository


class M2MModelFactory(
    saritasa_sqlalchemy_tools.AsyncSQLAlchemyModelFactory[
        example_app.repositories.M2MModelRepository.model,
        example_app.repositories.M2MModelRepository,
    ],
):
    """Factory to generate M2MModel."""

    class Meta:
        model = example_app.models.M2MModel
        repository = example_app.repositories.M2MModelRepository
        sub_factories: typing.ClassVar = {
            "related_model": "tests.factories.RelatedModelFactory",
            "test_model": "tests.factories.TestModelFactory",
        }
