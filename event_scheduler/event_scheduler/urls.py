from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from events.views import EventViewSet

# Swagger imports
from rest_framework.schemas import get_schema_view
from drf_yasg.views import get_schema_view as get_yasg_schema_view
from drf_yasg import openapi
from django.http import JsonResponse

router = DefaultRouter()
router.register(r'events', EventViewSet)

# Health check view
def health_check(request):
    return JsonResponse({"status": "ok"})

schema_view = get_yasg_schema_view(
    openapi.Info(
        title="Event Scheduler API",
        default_version='v1',
        description="API documentation for Event Scheduler",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),  # For logout
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('health/', health_check, name='health_check'),
]