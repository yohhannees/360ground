from django.shortcuts import render
from django.template import loader
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.views import View

class HomeView(View):
    def get(self, request):
        return render(request, 'home.html', {})

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
