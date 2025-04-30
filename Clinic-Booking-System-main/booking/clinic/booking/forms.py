from django import forms
from .models import Appointment

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your Email'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Your Message'
    }))

class SubscriptionForm(forms.Form):
    email = forms.EmailField(label='Your email', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['user', 'time', 'day', 'service']  # custom field order
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'time': forms.Select(attrs={'class': 'form-select'}),
            'day': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Select a date'
            }),
            'service': forms.Select(attrs={'class': 'form-select'}),
        }

