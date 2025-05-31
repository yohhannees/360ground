import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Event, EventInstance

User = get_user_model()

class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
            
        self.room_group_name = f'user_{self.user.id}_events'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'subscribe':
                event_id = data.get('event_id')
                if event_id:
                    await self.channel_layer.group_add(
                        f'event_{event_id}',
                        self.channel_name
                    )
                    await self.send(text_data=json.dumps({
                        'type': 'subscription_success',
                        'event_id': event_id
                    }))
            
            elif action == 'unsubscribe':
                event_id = data.get('event_id')
                if event_id:
                    await self.channel_layer.group_discard(
                        f'event_{event_id}',
                        self.channel_name
                    )
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def event_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'event_update',
            'event': event['event']
        }))
    
    async def instance_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'instance_update',
            'instance': event['instance']
        }))
    
    async def subscription_success(self, event):
        await self.send(text_data=json.dumps({
            'type': 'subscription_success',
            'event_id': event['event_id']
        }))
    
    async def error_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': event['message']
        }))