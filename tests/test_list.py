import pytest
import pytest_lazy_fixtures
import saritasa_sqlalchemy_tools

import example_app
import fastapi_rest_framework

from . import factories, shortcuts


@pytest.mark.parametrize(
    "user",
    [
        None,
        pytest_lazy_fixtures.lf("user_jwt_data"),
    ],
)
async def test_list_api(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user: shortcuts.UserData | None,
    repository: example_app.repositories.TestModelRepository,
    test_model_list: list[example_app.models.TestModel],
) -> None:
    """Test list API."""
    response = await api_client_factory(user).get(
        lazy_url(action_name="list"),
    )
    if not fastapi_rest_framework.testing.validate_auth_required_response(
        response,
    ):
        return

    response_data = (
        fastapi_rest_framework.testing.extract_paginated_result_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.list_schema,
        )
    )
    assert response_data.count == len(test_model_list), response_data


@pytest.mark.parametrize(
    argnames=[
        "limit",
        "offset",
        "expected_count",
    ],
    argvalues=[
        # limit and offset in allowed range
        [
            2,
            2,
            2,
        ],
        # offset is greater than instances counts
        [
            2,
            10,
            0,
        ],
        # limit is greater than count of instances starting from `offset`
        [
            5,
            4,
            1,
        ],
    ],
)
@pytest.mark.usefixtures("test_model_list")
async def test_list_api_pagination(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    limit: int,
    offset: int,
    expected_count: int,
) -> None:
    """Test that pagination for list API works correctly."""
    response = await api_client_factory(user_jwt_data).get(
        lazy_url(action_name="list"),
        params={
            "limit": limit,
            "offset": offset,
        },
    )
    response_data = (
        fastapi_rest_framework.testing.extract_paginated_result_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.list_schema,
        )
    )
    assert len(response_data.results) == expected_count


@pytest.mark.usefixtures("test_model_list")
async def test_list_api_pagination_negative_offset(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
) -> None:
    """Test that pagination for list API works correctly on negative offset."""
    response = await api_client_factory(user_jwt_data).get(
        lazy_url(action_name="list"),
        params={
            "limit": 10,
            "offset": -10,
        },
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="query.offset",
    )
    assert (
        response_data.detail == "Input should be greater than or equal to 0"
    ), response_data


async def test_list_api_search_filter(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    test_model_list: list[example_app.models.TestModel],
    repository: example_app.repositories.TestModelRepository,
) -> None:
    """Test search filter."""
    test_model = await factories.TestModelFactory.create_async(
        session=repository.db_session,
        text="1" * 100,
    )
    expected_instances = await repository.fetch_all(
        where=[
            saritasa_sqlalchemy_tools.transform_search_filter(
                example_app.models.TestModel,
                search_fields=[
                    "text",
                    "id",
                ],
                value=test_model.text,
            ),
        ],
        ordering_clauses=["id"],
    )
    assert len(expected_instances) == 1
    response = await api_client_factory(user_jwt_data).get(
        lazy_url(action_name="list"),
        params={
            "search": test_model.text,
        },
    )
    response_data = (
        fastapi_rest_framework.testing.extract_paginated_result_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.list_schema,
        )
    )

    assert len(response_data.results) == 1
    assert expected_instances[0].id == response_data.results[0].id


async def test_filter_in(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    test_model_list: list[example_app.models.TestModel],
) -> None:
    """Test filter `in`."""
    filter_value = [test_model_list[0].text, test_model_list[3].text]
    filtered_models = list(
        filter(
            lambda instance: instance.text
            in [test_model_list[0].text, test_model_list[3].text],
            test_model_list,
        ),
    )
    response = await api_client_factory(user_jwt_data).get(
        lazy_url(action_name="list"),
        params={
            "text__in": filter_value,
            "order_by": "id",
        },
    )
    response_data = (
        fastapi_rest_framework.testing.extract_paginated_result_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.list_schema,
        )
    )
    assert len(response_data.results) == 2
    assert (
        response_data.results[0].id,
        response_data.results[1].id,
    ) == (
        filtered_models[0].id,
        filtered_models[1].id,
    ), response_data


async def test_filter_gte(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    test_model_list: list[example_app.models.TestModel],
) -> None:
    """Test filter `gte`."""
    max_num = max(test_model.number for test_model in test_model_list)
    response = await api_client_factory(user_jwt_data).get(
        lazy_url(action_name="list"),
        params={
            "number__gte": max_num,
            "order_by": "id",
        },
    )
    response_data = (
        fastapi_rest_framework.testing.extract_paginated_result_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.list_schema,
        )
    )
    assert len(response_data.results) == 1
    assert response_data.results[0].number == max_num


async def test_filter_custom_filter(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    test_model_list: list[example_app.models.TestModel],
) -> None:
    """Test custom filter."""
    filtered_models = list(
        filter(
            lambda instance: instance.boolean,
            test_model_list,
        ),
    )
    response = await api_client_factory(user_jwt_data).get(
        lazy_url(action_name="list"),
        params={
            "is_boolean_condition_true": True,
            "order_by": "id",
        },
    )
    response_data = (
        fastapi_rest_framework.testing.extract_paginated_result_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.list_schema,
        )
    )
    assert len(response_data.results) == len(filtered_models)
    expected_ids = [test_model.id for test_model in filtered_models]
    actual_ids = [test_model.id for test_model in response_data.results]
    assert expected_ids == actual_ids, response_data


@pytest.mark.usefixtures("test_model_list")
async def test_filter_m2m(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    test_model: example_app.models.TestModel,
    repository: example_app.repositories.TestModelRepository,
) -> None:
    """Test filter related to m2m fields."""
    related_model = await factories.RelatedModelFactory.create_async(
        session=repository.db_session,
    )
    await factories.M2MModelFactory.create_batch_async(
        session=repository.db_session,
        size=5,
        test_model_id=test_model.id,
        related_model_id=related_model.id,
    )
    await factories.M2MModelFactory.create_batch_async(
        session=repository.db_session,
        test_model_id=test_model.id,
        size=5,
    )
    response = await api_client_factory(user_jwt_data).get(
        lazy_url(action_name="list"),
        params={
            "m2m_related_models_ids__in": [related_model.id],
            "order_by": "id",
        },
    )

    response_data = (
        fastapi_rest_framework.testing.extract_paginated_result_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.list_schema,
        )
    )
    assert len(response_data.results) == 1
    assert response_data.results[0].id == test_model.id


async def test_list_reverse_ordering(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    test_model_list: list[example_app.models.TestModel],
) -> None:
    """Test reverse ordering."""
    response = await api_client_factory(user_jwt_data).get(
        lazy_url(action_name="list"),
        params={
            "order_by": "-id",
        },
    )
    response_data = (
        fastapi_rest_framework.testing.extract_paginated_result_from_response(
            response=response,
            schema=example_app.views.TestModelAPIView.list_schema,
        )
    )
    assert len(response_data.results) == 5
    for actual, expected in zip(
        response_data.results,
        test_model_list[::-1],
        strict=False,
    ):
        assert actual.id == expected.id


async def test_list_invalid_value_in_filter(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    test_model_list: list[example_app.models.TestModel],
) -> None:
    """Test handling of invalid value in filter."""
    response = await api_client_factory(user_jwt_data).get(
        lazy_url(action_name="list"),
        params={
            "is_boolean_condition_true": "invalid",
        },
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="query.is_boolean_condition_true",
    )
    assert (
        response_data.detail
        == "Input should be a valid boolean, unable to interpret input"
    ), response_data


async def test_list_invalid_value_in_filter_body(
    lazy_url: fastapi_rest_framework.testing.LazyUrl,
    api_client_factory: shortcuts.AuthApiClientFactory,
    user_jwt_data: shortcuts.UserData,
    test_model_list: list[example_app.models.TestModel],
) -> None:
    """Test handling of invalid value in filter's body.

    Test that we correctly handle validation error if it's happen in whole
    model validation method.

    """
    response = await api_client_factory(user_jwt_data).get(
        lazy_url(action_name="list"),
        params={"search": "invalid", "is_boolean_condition_true": True},
    )
    response_data = fastapi_rest_framework.testing.extract_error_from_response(
        response=response,
        field="query",
    )
    assert (
        response_data.detail
        == "Value error, Invalid can't be used with condition"
    ), response_data
