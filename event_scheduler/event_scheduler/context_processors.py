from django.conf import settings
from django.utils import timezone

def site_info(request):
    """
    Add site-wide information to the template context.
    """
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Event Scheduler'),
        'SITE_URL': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        'CURRENT_YEAR': timezone.now().year,
        'DEBUG': settings.DEBUG,
    }

def user_info(request):
    """
    Add user-related information to the template context.
    """
    user = request.user if hasattr(request, 'user') else None
    return {
        'current_user': user,
        'is_authenticated': user.is_authenticated if user else False,
    }
