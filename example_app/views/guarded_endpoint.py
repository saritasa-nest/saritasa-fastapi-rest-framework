import typing

import fastapi

import fastapi_rest_framework

from .. import security

router = fastapi.APIRouter(
    prefix="/guarded-endpoint",
)


@router.get(
    "/",
    responses=fastapi_rest_framework.DEFAULT_ERROR_RESPONSES,
    dependencies=[
        fastapi.Depends(
            fastapi_rest_framework.get_permissions_dependency(
                action="list",
                permissions=(security.AllowPermission[typing.Any](),),
                user_dependency=security.UserAuth,  # type: ignore
            ),
        ),
    ],
)
def guarded_endpoint() -> None:
    """Do something."""
