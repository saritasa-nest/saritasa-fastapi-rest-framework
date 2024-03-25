import collections.abc
import http
import typing

import fastapi


def action(
    method: str = http.HTTPMethod.GET,
    detail: bool = False,
    paginated: bool = False,
    status_code: int = http.HTTPStatus.OK,
    response_class: type = fastapi.responses.JSONResponse,
) -> collections.abc.Callable[
    [collections.abc.Callable[..., typing.Any]],
    typing.Any,
]:
    """Add action endpoint to view."""

    def _action(func: collections.abc.Callable[..., typing.Any]) -> typing.Any:
        func.action_config = {  # type: ignore
            "method": method.lower(),
            "detail": detail,
            "paginated": paginated,
            "status_code": status_code,
            "response_class": response_class,
        }
        return func

    return _action
