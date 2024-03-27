import typing

import factory
import factory.fuzzy
import saritasa_sqlalchemy_tools

import example_app


class UserJWTDataFactory(factory.Factory):
    """Factory to generate test UserJWTData instance."""

    id = factory.Faker(
        "pyint",
        min_value=1,
    )
    allow = True

    class Meta:
        model = example_app.security.UserJWTData


class TestModelFactory(
    saritasa_sqlalchemy_tools.AsyncSQLAlchemyModelFactory[
        example_app.models.TestModel
    ],
):
    """Factory to generate TestModel."""

    text = factory.Faker(
        "pystr",
        min_chars=1,
        max_chars=30,
    )
    text_enum = factory.fuzzy.FuzzyChoice(
        example_app.models.TestModel.TextEnum,
    )
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

    class Meta:
        model = example_app.models.TestModel
        repository = example_app.repositories.TestModelRepository
        sub_factories: typing.ClassVar = {
            "related_model": "tests.factories.RelatedModelFactory",
            "related_models": ("tests.factories.RelatedModelFactory", 5),
        }


class SoftDeleteTestModelFactory(
    saritasa_sqlalchemy_tools.AsyncSQLAlchemyModelFactory[
        example_app.models.SoftDeleteTestModel
    ],
):
    """Factory to generate SoftDeleteTestModel."""

    text = factory.Faker(
        "pystr",
        min_chars=200,
        max_chars=250,
    )
    text_enum = factory.fuzzy.FuzzyChoice(
        example_app.models.TestModel.TextEnum,
    )
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

    class Meta:
        model = example_app.models.SoftDeleteTestModel
        repository = example_app.repositories.SoftDeleteTestModelRepository


class RelatedModelFactory(
    saritasa_sqlalchemy_tools.AsyncSQLAlchemyModelFactory[
        example_app.models.RelatedModel
    ],
):
    """Factory to generate RelatedModel."""

    class Meta:
        model = example_app.models.RelatedModel
        repository = example_app.repositories.RelatedModelRepository


class M2MModelFactory(
    saritasa_sqlalchemy_tools.AsyncSQLAlchemyModelFactory[
        example_app.models.M2MModel
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
