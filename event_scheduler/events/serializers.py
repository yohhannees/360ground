from rest_framework import serializers
from django.utils import timezone
from .models import Event, EventInstance
from dateutil.rrule import rrulestr
from datetime import timedelta

class EventInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventInstance
        fields = ['id', 'start_datetime', 'end_datetime', 'is_cancelled']

class EventSerializer(serializers.ModelSerializer):
    instances = EventInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_datetime', 'end_datetime',
            'is_recurring', 'frequency', 'interval', 'byweekday', 'bymonthday',
            'bysetpos', 'until', 'created_at', 'updated_at', 'instances'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        if data['end_datetime'] <= data['start_datetime']:
            raise serializers.ValidationError("End datetime must be after start datetime.")
        if data.get('is_recurring'):
            if not data.get('frequency'):
                raise serializers.ValidationError("Frequency is required for recurring events.")
            if data.get('until') and data['until'] <= data['start_datetime']:
                raise serializers.ValidationError("Until date must be after start datetime.")
        return data

    def create(self, validated_data):
        event = Event.objects.create(user=self.context['request'].user, **validated_data)
        if event.is_recurring:
            self._generate_instances(event)
        return event

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if instance.is_recurring:
            instance.instances.all().delete()  # Clear old instances
            self._generate_instances(instance)
        return instance

    def _generate_instances(self, event):
        from dateutil.rrule import rrulestr
        rrule_str = f"DTSTART:{event.start_datetime.strftime('%Y%m%dT%H%M%S')}\nRRULE:"
        if event.frequency:
            rrule_str += f"FREQ={event.frequency};INTERVAL={event.interval}"
        if event.byweekday:
            rrule_str += f";BYDAY={event.byweekday}"
        if event.bymonthday:
            rrule_str += f";BYMONTHDAY={event.bymonthday}"
        if event.bysetpos:
            rrule_str += f";BYSETPOS={event.bysetpos}"
        if event.until:
            rrule_str += f";UNTIL={event.until.strftime('%Y%m%dT%H%M%S')}"
        rrule = rrulestr(rrule_str, dtstart=event.start_datetime)
        duration = event.end_datetime - event.start_datetime
        for start in rrule:
            if start > event.until if event.until else False:
                break
            EventInstance.objects.create(
                event=event,
                start_datetime=start,
                end_datetime=start + duration
            )