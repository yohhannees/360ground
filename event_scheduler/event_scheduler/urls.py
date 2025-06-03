from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from events.views import (
    EventViewSet, 
    EventListView, 
    EventDetailView, 
    EventCreateView, 
    EventUpdateView, 
    EventDeleteView,
    CalendarView,
    event_instances,
    cancel_instance,
    signup
)

# Swagger imports
from rest_framework.schemas import get_schema_view
from drf_yasg.views import get_schema_view as get_yasg_schema_view
from drf_yasg import openapi
from django.http import JsonResponse
from event_scheduler.views import HomeView

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

# Template-based URL patterns
template_urls = [
    path('', EventListView.as_view(), name='event-list'),
    path('events/create/', EventCreateView.as_view(), name='event-create'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('events/<int:pk>/edit/', EventUpdateView.as_view(), name='event-update'),
    path('events/<int:pk>/delete/', EventDeleteView.as_view(), name='event-delete'),
    # path('calendar/', CalendarView.as_view(), name='event-calendar'),
    path('events/<int:event_id>/instances/', event_instances, name='event-instances'),
    path('api/events/instance/<int:instance_id>/cancel/', cancel_instance, name='cancel-instance'),
]

# Authentication URL patterns
auth_urls = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', signup, name='signup'),
]

urlpatterns = [

    
    # API URLs
    path('', HomeView.as_view(), name='home'),
    path('events/', EventListView.as_view(), name='event-list'),
    path('calendar/', CalendarView.as_view(), name='event-calendar'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/events/', include(router.urls)),
    
    # Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Template-based URLs
    path('', include((template_urls, 'events'), namespace='events')),
    
    # Authentication URLs
    path('accounts/', include(auth_urls)),
    
    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'event_scheduler.views.handler404'
handler500 = 'event_scheduler.views.handler500'