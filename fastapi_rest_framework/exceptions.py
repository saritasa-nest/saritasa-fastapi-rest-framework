import collections.abc
import http

import fastapi


class PermissionException(fastapi.HTTPException):
    """Raise if user has no permission for object/action."""

    def __init__(
        self,
        status_code: http.HTTPStatus = http.HTTPStatus.FORBIDDEN,
        detail: str | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)


class UnauthorizedException(fastapi.HTTPException):
    """Raise if user is unauthorized."""

    def __init__(
        self,
        status_code: http.HTTPStatus = http.HTTPStatus.UNAUTHORIZED,
        detail: str | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(fastapi.HTTPException):
    """Raise if object not found."""

    def __init__(
        self,
        status_code: http.HTTPStatus = http.HTTPStatus.NOT_FOUND,
        detail: str | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)


class PermissionActionException(fastapi.HTTPException):
    """Raise if user has no permissions for action."""

    def __init__(
        self,
        required_permissions: collections.abc.Sequence[str],
        status_code: http.HTTPStatus = http.HTTPStatus.FORBIDDEN,
    ) -> None:
        self.required_permissions = required_permissions
        super().__init__(
            status_code=status_code,
            detail=(
                "User has no permissions for this action. "
                f"Required permissions: {','.join(required_permissions)}."
            ),
        )
