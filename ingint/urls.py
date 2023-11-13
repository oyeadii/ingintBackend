from drf_yasg import openapi
from django.conf import settings
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view


schema_view = get_schema_view(
    openapi.Info(
        title="Ingint APIs",
        default_version='v1.0',
        description="API documentation for Ingint 1.0",
        terms_of_service="",
        contact=openapi.Contact(email="aditya@dotnitron.com"),
        license=openapi.License(name="Closed Source"),
    ),
    url=settings.HOST_SERVER,
    public=True,
    permission_classes=[permissions.AllowAny],
)
urlpatterns = [
    path('api/user/', include('user.urls')),
    path('api/analytics/', include('data_analytics.urls')),
]
if settings.ENVI != 'PROD':
    urlpatterns.append(
        path(
            'swagger/',
            schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
        )

