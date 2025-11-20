from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from config.api.health import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Health check
    path('api/health/', health_check, name='health-check'),
    
    # Documentation API 
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)), # Redirect to the swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    
    # API REST 
    path('api/', include('apps.notes.urls')),
    path('api/', include('apps.todos.urls')),
]