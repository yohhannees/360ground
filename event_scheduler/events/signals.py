from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Event, EventInstance

@receiver(post_save, sender=Event)
def event_created_or_updated(sender, instance, created, **kwargs):
    from .serializers import EventSerializer
    serializer = EventSerializer(instance)
    event_data = serializer.data
    
    channel_layer = get_channel_layer()
    group_name = f'user_{instance.user_id}_events'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'event_update',
            'event': event_data
        }
    )
    
    if not created:
        event_group = f'event_{instance.id}'
        async_to_sync(channel_layer.group_send)(
            event_group,
            {
                'type': 'event_update',
                'event': event_data
            }
        )

@receiver(post_save, sender=EventInstance)
def instance_created_or_updated(sender, instance, created, **kwargs):
    from .serializers import EventInstanceSerializer
    serializer = EventInstanceSerializer(instance)
    instance_data = serializer.data
    
    channel_layer = get_channel_layer()
    group_name = f'user_{instance.event.user_id}_events'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'instance_update',
            'instance': instance_data
        }
    )
    
    event_group = f'event_{instance.event_id}'
    async_to_sync(channel_layer.group_send)(
        event_group,
        {
            'type': 'instance_update',
            'instance': instance_data
        }
    )

@receiver(post_delete, sender=Event)
def event_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    group_name = f'user_{instance.user_id}_events'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'event_deleted',
            'event_id': instance.id
        }
    )

@receiver(post_delete, sender=EventInstance)
def instance_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    group_name = f'user_{instance.event.user_id}_events'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'instance_deleted',
            'instance_id': instance.id,
            'event_id': instance.event_id
        }
    )
    
    event_group = f'event_{instance.event_id}'
    async_to_sync(channel_layer.group_send)(
        event_group,
        {
            'type': 'instance_deleted',
            'instance_id': instance.id,
            'event_id': instance.event_id
        }
    )