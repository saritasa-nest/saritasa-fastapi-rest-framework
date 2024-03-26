import fastapi_rest_framework

from .. import repositories


class TestModelValidator(
    fastapi_rest_framework.BaseModelValidator[
        repositories.TestModelRepository,
        repositories.TestModelRepository.model,
    ],
):
    """Validate test model data."""
