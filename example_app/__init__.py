import fastapi

import fastapi_rest_framework

from . import (
    db,
    models,
    repositories,
    schemas,
    security,
    views,
)

router = fastapi.APIRouter(
    redirect_slashes=False,
)
router.include_router(views.TestModelAPIView.router)

fastapi_app = fastapi.FastAPI(
    title="Test APP",
)
fastapi_app.include_router(router)
fastapi_app.exception_handler(fastapi.HTTPException)(
    fastapi_rest_framework.http_exception_handler,
)
fastapi_app.exception_handler(fastapi_rest_framework.ValidationError)(
    fastapi_rest_framework.validation_error_exception_handler,
)
fastapi_app.exception_handler(fastapi.exceptions.RequestValidationError)(
    fastapi_rest_framework.pydantic_validation_error_exception_handler,
)
