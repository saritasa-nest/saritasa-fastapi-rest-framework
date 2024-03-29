import typing

import fastapi_rest_framework

from .. import repositories
from . import core


class TestModelInteractor(
    core.Interactor[
        repositories.TestModelRepository.model,
        repositories.TestModelRepository,
    ],
):
    """Save test model api data into database."""

    model = repositories.TestModelRepository.model

    m2m_create_update_config: typing.ClassVar[
        dict[str, fastapi_rest_framework.M2MCreateUpdateConfig]
    ] = {
        "m2m_related_models_ids": fastapi_rest_framework.M2MCreateUpdateConfig(
            m2m_repository_class=repositories.M2MModelRepository,
            m2m_repository_model=repositories.M2MModelRepository.model,
            instance_m2m_field="test_model_id",
            link_field="related_model_id",
            instance_m2m_relationship_field="m2m_related_models",
            instance_m2m_relationship_pk_field="id",
        ),
    }
