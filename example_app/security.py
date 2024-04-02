import datetime
import typing

import fastapi
import fastapi.security
import pydantic

import fastapi_rest_framework


class UserJWTData(pydantic.BaseModel):
    """Representation of user data from JWT Token."""

    id: int = 0
    allow: bool = False
    # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.6
    iat: datetime.datetime = datetime.datetime.min
    # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.4
    exp: datetime.datetime = datetime.datetime.max

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def is_anonymous(self) -> bool:
        """If user_id is more than 0, then it's not anonymous user."""
        return self.id <= 0

    @pydantic.field_serializer("iat", "exp")
    def serialize_datetime(
        self,
        value: datetime.datetime,
        info: pydantic.FieldSerializationInfo,
    ) -> int:
        """Serialize datetime."""
        return int(value.timestamp())


class JWTAuthClass(
    fastapi_rest_framework.jwt.SentryJWTTokenAuthentication[UserJWTData],
):
    """Auth class."""

    user_model: type[UserJWTData] = UserJWTData


jwt_private_key, jwt_public_key = (
    fastapi_rest_framework.testing.generate_private_and_public_key_for_rs256_jwt()
)
JWTAuth = JWTAuthClass(
    jwt_public_key=jwt_public_key,
    jwt_private_key=jwt_private_key,
    jwt_algorithms=("RS256",),
)

UserAuth: typing.TypeAlias = typing.Annotated[
    UserJWTData,
    fastapi.Depends(JWTAuth),
]


class BasePermission(
    fastapi_rest_framework.BasePermission[
        fastapi_rest_framework.PermissionInstanceT,
        UserJWTData,
    ],
    typing.Generic[fastapi_rest_framework.PermissionInstanceT],
):
    """Base permission class."""


class AuthRequiredPermission(
    BasePermission[fastapi_rest_framework.PermissionInstanceT,],
    typing.Generic[fastapi_rest_framework.PermissionInstanceT,],
):
    """Check that user is authenticated."""

    async def _check_permission(
        self,
        user: UserJWTData,
        action: str,
        context: fastapi_rest_framework.ContextType,
        request_data: fastapi_rest_framework.RequestData,
    ) -> None:
        if user.is_anonymous:
            raise fastapi_rest_framework.UnauthorizedException()


class AllowPermission(
    BasePermission[fastapi_rest_framework.PermissionInstanceT,],
    typing.Generic[fastapi_rest_framework.PermissionInstanceT,],
):
    """Check that user is allowed."""

    async def _check_permission(
        self,
        user: UserJWTData,
        action: str,
        context: fastapi_rest_framework.ContextType,
        request_data: fastapi_rest_framework.RequestData,
    ) -> None:
        if not user.allow:
            raise fastapi_rest_framework.PermissionException(
                detail="User is not allowed",
            )
