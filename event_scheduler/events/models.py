from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Event(models.Model):
    FREQUENCY_CHOICES = (
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    )

    WEEKDAY_CHOICES = (
        ('MO', 'Monday'),
        ('TU', 'Tuesday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
        ('SU', 'Sunday'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_recurring = models.BooleanField(default=False)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, blank=True)
    interval = models.PositiveIntegerField(default=1, help_text="Recur every n-th day/week/month/year")
    byweekday = models.CharField(max_length=50, blank=True, help_text="Comma-separated weekdays, e.g., 'MO,WE'")
    bymonthday = models.IntegerField(null=True, blank=True, help_text="Day of the month, e.g., 15")
    bysetpos = models.IntegerField(null=True, blank=True, help_text="e.g., -1 for last, 2 for second")
    until = models.DateTimeField(null=True, blank=True, help_text="Recurrence end date")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class EventInstance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='instances')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_cancelled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.event.title} - {self.start_datetime}"