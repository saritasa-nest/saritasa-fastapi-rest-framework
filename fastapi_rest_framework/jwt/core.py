import datetime
import enum
import typing

import fastapi.security
import jwt
import pydantic

from .. import exceptions, metrics


class TokenType(enum.StrEnum):
    """Representation of JWT token types."""

    access = "access"
    refresh = "refresh"


class BaseJWTData(pydantic.BaseModel):
    """Representation of base data for JWT tokens."""

    token_type: TokenType = TokenType.access
    # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.6
    iat: datetime.datetime = datetime.datetime.min + datetime.timedelta(days=1)
    # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.4
    exp: datetime.datetime = datetime.datetime.max - datetime.timedelta(days=1)

    @pydantic.field_serializer("iat", "exp")
    def serialize_datetime(
        self,
        value: datetime.datetime,
        info: pydantic.FieldSerializationInfo,
    ) -> int:
        """Serialize datetime."""
        return int(value.timestamp())


UserJWTType = typing.TypeVar("UserJWTType", bound=BaseJWTData)


class JWTTokenAuthentication(
    pydantic.BaseModel,
    typing.Generic[UserJWTType],
):
    """Perform jwt token authentication."""

    jwt_public_key: str
    jwt_private_key: str | None = None
    jwt_algorithms: tuple[str, ...]
    user_model: type[UserJWTType]

    def __hash__(self) -> int:
        """Create hash for fastapi deps."""
        return hash((type(self), *tuple(self.__dict__.values())))

    @metrics.tracker
    def __call__(
        self,
        token: typing.Annotated[
            fastapi.security.HTTPAuthorizationCredentials | None,
            fastapi.Depends(fastapi.security.HTTPBearer(auto_error=False)),
        ] = None,
    ) -> UserJWTType:
        """Transform token into user data."""
        if not token:
            return self.user_model()
        return self.decode_access(token=token.credentials)

    @metrics.tracker
    def decode(self, token: str) -> UserJWTType:
        """Transform token into user data."""
        try:
            user_data = jwt.decode(
                jwt=token,
                key=self.jwt_public_key,
                algorithms=list(self.jwt_algorithms),
            )
            return self.on_user_auth(
                self.user_model.model_validate(user_data),
            )
        except (
            jwt.exceptions.ExpiredSignatureError
        ) as error:  # pragma: no cover
            raise exceptions.UnauthorizedException(
                detail="JWT Token is expired",
            ) from error
        except pydantic.ValidationError as error:  # pragma: no cover
            raise exceptions.UnauthorizedException(
                detail="Invalid JWT token body",
            ) from error
        except (
            ValueError,
            jwt.exceptions.InvalidTokenError,
        ) as error:  # pragma: no cover
            raise exceptions.UnauthorizedException(
                detail="Invalid JWT Token",
            ) from error

    @metrics.tracker
    def decode_access(self, token: str) -> UserJWTType:
        """Transform access token into user data."""
        decoded = self.decode(token=token)
        if decoded.token_type != TokenType.access:
            raise exceptions.UnauthorizedException(
                detail=f"Token type must be {TokenType.access}",
            )
        return decoded

    @metrics.tracker
    def decode_refresh(self, token: str) -> UserJWTType:
        """Transform refresh token into user data."""
        decoded = self.decode(token=token)
        if decoded.token_type != TokenType.refresh:
            raise exceptions.UnauthorizedException(
                detail=f"Token type must be {TokenType.refresh}",
            )
        return decoded

    @metrics.tracker
    def on_user_auth(self, user: UserJWTType) -> UserJWTType:
        """Perform action on auth authentication."""
        return user

    @metrics.tracker
    def generate_jwt_for_user(self, user: UserJWTType) -> str:
        """Generate JWT token for user."""
        if not self.jwt_private_key:  # pragma: no cover
            raise ValueError("JWT Private key is not set")
        return jwt.encode(
            payload=user.model_dump(mode="json"),
            key=self.jwt_private_key,
            algorithm=self.jwt_algorithms[0],
        )
