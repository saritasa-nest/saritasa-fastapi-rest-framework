import contextlib

from .core import JWTTokenAuthentication

with contextlib.suppress(ImportError):
    from .sentry import SentryJWTTokenAuthentication
