import saritasa_s3_tools

import fastapi_rest_framework


class S3ContextMixin:
    """Mixin which extracts s3 context."""

    def get_s3_client_from_context(
        self,
        context: fastapi_rest_framework.ContextType,
    ) -> saritasa_s3_tools.AsyncS3Client:
        """Extract s3 client from context."""
        if "s3_client" not in context:
            raise KeyError(
                "`s3_client` wasn't found in context",
            )  # pragma: no cover
        return context["s3_client"]
