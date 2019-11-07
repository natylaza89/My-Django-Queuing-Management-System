from datetime import date
from django.forms import ModelForm, DateInput, TimeInput, TimeField, DateField,  DateTimeInput, HiddenInput
from django import forms
from django.contrib.auth.models import User
from .models import Treatments


class TreatmentForm(ModelForm):
    #exclude = ['user', 'google_event_id']
  
    class Meta:
        model = Treatments
        fields = ['title', 'description', 'date', 'time']
        #fields = '__all__'
        widgets = {
          'date': DateInput(attrs={'type': 'date'}, format='%d/%m/%Y'),
          #'time': DateInput(attrs={'type': 'time'}, format='%H:%M'),
          'user': HiddenInput(),
        }

        labels = {
              "title": "כותרת",
              "description": "הערות",
              "date": "תאריך",
              "time": "שעה",
          }
