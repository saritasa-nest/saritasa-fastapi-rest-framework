import typing

import sentry_sdk

from .. import metrics, permissions
from . import core


class SentryJWTTokenAuthentication(
    core.JWTTokenAuthentication[permissions.UserT],
    typing.Generic[permissions.UserT],
):
    """JWT Authentication with sentry tracking."""

    def get_fields_to_remove(
        self,
        user: permissions.UserT,
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
    def on_user_auth(self, user: permissions.UserT) -> permissions.UserT:
        """Set user in sentry."""
        user = super().on_user_auth(user)
        field_to_remove = self.get_fields_to_remove(user)
        sentry_user_data = user.model_dump(exclude=field_to_remove)
        sentry_sdk.set_user(sentry_user_data)
        return user
