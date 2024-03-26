import typing

import fastapi.security
import jwt
import pydantic

from . import exceptions, permissions


class JWTTokenAuthentication(
    pydantic.BaseModel,
    typing.Generic[permissions.UserT],
):
    """Perform jwt token authentication."""

    jwt_public_key: str
    jwt_algorithms: tuple[str, ...]
    user_model: type[permissions.UserT]

    def __hash__(self) -> int:
        """Create hash for fastapi deps."""
        return hash((type(self), *tuple(self.__dict__.values())))

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
        except jwt.exceptions.ExpiredSignatureError as error:
            raise exceptions.UnauthorizedException(
                detail="JWT Token is expired",
            ) from error
        except pydantic.ValidationError as error:
            raise exceptions.UnauthorizedException(
                detail="Invalid JWT token body",
            ) from error
        except (ValueError, jwt.exceptions.InvalidTokenError) as error:
            raise exceptions.UnauthorizedException(
                detail="Invalid JWT Token",
            ) from error

    def on_user_auth(self, user: permissions.UserT) -> permissions.UserT:
        """Perform action on auth authentication."""
        return user
