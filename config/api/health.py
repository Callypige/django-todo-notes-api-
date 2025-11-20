from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "HEAD"])
def health_check(request: HttpRequest) -> JsonResponse:
    """
    Simple health check endpoint for Docker/monitoring.
    Returns 200 OK if the application is running.
    """
    return JsonResponse({
        "status": "healthy",
        "service": "django-todo-notes-api"
    })
