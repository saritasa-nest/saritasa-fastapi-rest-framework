import typing

import sentry_sdk

from .. import metrics
from . import core


class SentryJWTTokenAuthentication(
    core.JWTTokenAuthentication[core.UserJWTType],
    typing.Generic[core.UserJWTType],
):
    """JWT Authentication with sentry tracking."""

    def get_fields_to_remove(
        self,
        user: core.UserJWTType,
    ) -> (
        set[int]
        | set[str]
        | dict[int, typing.Any]
        | dict[str, typing.Any]
        | None
    ):
        """Get list of fields that should be removed from tracking."""
        return None

    @metrics.tracker
    def on_user_auth(self, user: core.UserJWTType) -> core.UserJWTType:
        """Set user in sentry."""
        user = super().on_user_auth(user)
        field_to_remove = self.get_fields_to_remove(user)
        sentry_user_data = user.model_dump(
            mode="json",
            exclude=field_to_remove,
        )
        sentry_sdk.set_user(sentry_user_data)
        return user
