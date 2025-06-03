from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
import pytz

class TimezoneMiddleware(MiddlewareMixin):
    """
    Middleware to handle user timezone settings.
    
    If the user is authenticated, it will use their timezone preference.
    Otherwise, it will use the default timezone from settings.
    """
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Get the user's timezone from their profile if available
            user_timezone = getattr(request.user, 'timezone', None)
            if user_timezone:
                try:
                    timezone.activate(pytz.timezone(user_timezone))
                except pytz.UnknownTimeZoneError:
                    timezone.deactivate()
            else:
                timezone.deactivate()
        else:
            timezone.deactivate()
        return None

    def process_response(self, request, response):
        timezone.deactivate()
        return response
