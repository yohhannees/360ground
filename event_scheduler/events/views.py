from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Event, EventInstance
from .serializers import EventSerializer, EventInstanceSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = ['rest_framework.permissions.IsAuthenticated']

    def get_queryset(self):
        queryset = Event.objects.filter(user=self.request.user)
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
        serializer.save(user=self.request.user)

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