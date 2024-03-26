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
