from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Event

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class EventForm(forms.ModelForm):
    is_recurring = forms.BooleanField(
        required=False,
        label='Is this a recurring event?',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'start_datetime', 'end_datetime',
            'is_recurring', 'frequency', 'interval', 'byweekday', 'bymonthday', 'bysetpos', 'until'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'interval': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'byweekday': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., MO,WE,FR'}),
            'bymonthday': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 31}),
            'bysetpos': forms.NumberInput(attrs={'class': 'form-control'}),
            'until': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['is_recurring'].initial = bool(self.instance.frequency)

    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        is_recurring = cleaned_data.get('is_recurring')
        frequency = cleaned_data.get('frequency')

        if start_datetime and end_datetime and end_datetime <= start_datetime:
            self.add_error('end_datetime', 'End time must be after start time')

        if is_recurring and not frequency:
            self.add_error('frequency', 'Frequency is required for recurring events')

        return cleaned_data