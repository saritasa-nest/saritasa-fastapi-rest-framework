import typing

import fastapi.security
import jwt
import pydantic

from .. import exceptions, metrics, permissions


class JWTTokenAuthentication(
    pydantic.BaseModel,
    typing.Generic[permissions.UserT],
):
    """Perform jwt token authentication."""

    jwt_public_key: str
    jwt_private_key: str | None = None
    jwt_algorithms: tuple[str, ...]
    user_model: type[permissions.UserT]

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
    ) -> permissions.UserT:
        """Transform token into user data."""
        if not token:
            return self.user_model()
        try:
            user_data = jwt.decode(
                jwt=token.credentials,
                key=self.jwt_public_key,
                algorithms=list(self.jwt_algorithms),
            )
            return self.on_user_auth(self.user_model.model_validate(user_data))
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
    def on_user_auth(self, user: permissions.UserT) -> permissions.UserT:
        """Perform action on auth authentication."""
        return user

    @metrics.tracker
    def generate_jwt_for_user(self, user: permissions.UserT) -> str:
        """Generate JWT token for user."""
        if not self.jwt_private_key:  # pragma: no cover
            raise ValueError("JWT Private key is not set")
        return jwt.encode(
            payload=user.model_dump(mode="json"),
            key=self.jwt_private_key,
            algorithm=self.jwt_algorithms[0],
        )
