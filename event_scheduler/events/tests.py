
# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from .models import Event, EventInstance
from datetime import timedelta

class EventTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.token = self.client.post('/api/token/', {'username': 'testuser', 'password': 'testpass'}).json()['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.event = Event.objects.create(
            user=self.user,
            title='Test Event',
            description='Test Description',
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            is_recurring=True,
            frequency='WEEKLY',
            interval=1,
            byweekday='MO,WE',
            until=timezone.now() + timedelta(days=30)
        )

    def test_create_single_event(self):
        data = {
            'title': 'Single Event',
            'description': 'One-off event',
            'start_datetime': (timezone.now() + timedelta(days=2)).isoformat(),
            'end_datetime': (timezone.now() + timedelta(days=2, hours=1)).isoformat(),
            'is_recurring': False
        }
        response = self.client.post('/api/events/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 2)

    def test_create_recurring_event(self):
        data = {
            'title': 'Recurring Event',
            'description': 'Weekly event',
            'start_datetime': (timezone.now() + timedelta(days=3)).isoformat(),
            'end_datetime': (timezone.now() + timedelta(days=3, hours=1)).isoformat(),
            'is_recurring': True,
            'frequency': 'WEEKLY',
            'interval': 2,
            'byweekday': 'MO,FR',
            'until': (timezone.now() + timedelta(days=60)).isoformat()
        }
        response = self.client.post('/api/events/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(EventInstance.objects.filter(event__title='Recurring Event').exists())

    def test_filter_events_by_date(self):
        response = self.client.get(
            f'/api/events/?start={(timezone.now() + timedelta(days=1)).isoformat()}'
            f'&end={(timezone.now() + timedelta(days=2)).isoformat()}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_cancel_instance(self):
        instance = EventInstance.objects.create(
            event=self.event,
            start_datetime=self.event.start_datetime,
            end_datetime=self.event.end_datetime
        )
        response = self.client.post(f'/api/events/{self.event.id}/cancel_instance/', {'instance_id': instance.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        instance.refresh_from_db()
        self.assertTrue(instance.is_cancelled)