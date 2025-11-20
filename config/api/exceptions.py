import logging
from typing import Any, Dict, Optional

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def _build_payload(
    detail: str,
    code: Optional[str],
    errors: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "detail": detail,
        "code": (code or "error"),
        "errors": errors or None,
    }


def custom_exception_handler(exc, context):
    """Return a normalized error response for all API exceptions."""
    if isinstance(exc, DjangoValidationError):
        exc = DRFValidationError(detail=exc.message_dict if hasattr(exc, "message_dict") else exc.messages)

    response = drf_exception_handler(exc, context)

    if response is not None:
        data = response.data or {}
        detail = data.pop("detail", None)
        errors = data if data else None

        if detail is None:
            if isinstance(exc, DRFValidationError):
                detail = "Validation error"
            else:
                detail = "An unexpected error occurred."

        code = getattr(exc, "default_code", None)
        response.data = _build_payload(detail=detail, code=code, errors=errors)
        return response

    logger.exception("Unhandled exception in API layer", exc_info=exc)

    return Response(
        _build_payload(detail="Internal server error", code="server_error"),
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

