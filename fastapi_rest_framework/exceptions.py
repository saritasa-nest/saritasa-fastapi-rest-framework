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
