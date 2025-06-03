from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
from django.views import View
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Event, EventInstance
from .forms import EventForm, SignUpForm
from .serializers import EventSerializer, EventInstanceSerializer

# REST API Views
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start and end:
            queryset = queryset.filter(
                start_datetime__lte=end,
                end_datetime__gte=start
            ) | queryset.filter(
                instances__start_datetime__lte=end,
                instances__end_datetime__gte=start,
                instances__is_cancelled=False
            )
        return queryset.order_by('start_datetime')

    def perform_create(self, serializer):
        # The user is already set in the serializer's create method
        serializer.save()

    @action(detail=True, methods=['post'])
    def cancel_instance(self, request, pk=None):
        instance_id = request.data.get('instance_id')
        try:
            instance = EventInstance.objects.get(id=instance_id, event__id=pk, event__user=request.user)
            instance.is_cancelled = True
            instance.save()
            return Response({'status': 'instance cancelled'})
        except EventInstance.DoesNotExist:
            return Response({'error': 'Instance not found'}, status=404)

# Template-based Views
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10
    
    def get_queryset(self):
        return Event.objects.filter(user=self.request.user).order_by('-start_datetime')

class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    
    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Event created successfully!')
        return response
    
    def get_success_url(self):
        return reverse('events:event-detail', kwargs={'pk': self.object.pk})

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Event updated successfully!')
        return response
    
    def get_success_url(self):
        return reverse('events:event-detail', kwargs={'pk': self.object.pk})

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:event-list')
    
    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Event deleted successfully!')
        return super().delete(request, *args, **kwargs)

class CalendarView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'events/calendar.html')

@login_required
def event_instances(request, event_id):
    event = get_object_or_404(Event, id=event_id, user=request.user)
    instances = event.instances.filter(
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')[:50]  # Limit to next 50 instances
    
    data = [{
        'id': instance.id,
        'start_datetime': instance.start_datetime.isoformat(),
        'end_datetime': instance.end_datetime.isoformat(),
        'is_cancelled': instance.is_cancelled
    } for instance in instances]
    
    return JsonResponse(data, safe=False)

@require_http_methods(["POST"])
@login_required
def cancel_instance(request, instance_id):
    instance = get_object_or_404(
        EventInstance, 
        id=instance_id, 
        event__user=request.user
    )
    instance.is_cancelled = True
    instance.save()
    return JsonResponse({'status': 'success'})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('event-calendar')  # Redirect to calendar after signup
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})