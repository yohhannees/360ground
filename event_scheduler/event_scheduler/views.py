from django.shortcuts import render
from django.template import loader
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.views import View
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from events.models import Event
class HomeView(View):
    def get(self, request):
        return render(request, 'home.html', {})
# In events/views.p
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
       return Event.objects.filter(user=self.request.user).order_by('-start_datetime')
class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'  # Make sure this is set
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)

def handler404(request, exception, template_name='404.html'):
    """
    Custom 404 error handler.
    """
    context = {
        'title': 'Page Not Found',
        'message': 'The page you are looking for does not exist.',
        'status_code': 404
    }
    
    template = loader.get_template(template_name)
    return HttpResponseNotFound(template.render(context, request))

def handler500(request, template_name='500.html'):
    """
    Custom 500 error handler.
    """
    context = {
        'title': 'Server Error',
        'message': 'An error occurred while processing your request.',
        'status_code': 500
    }
    
    template = loader.get_template(template_name)
    return HttpResponseServerError(template.render(context, request))
