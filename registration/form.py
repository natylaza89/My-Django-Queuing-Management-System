from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="כתובת מייל")
    first_name = forms.CharField(required=True, label="שם פרטי")
    last_name = forms.CharField(required=True, label="שם משפחה")
    
    # nested namespace for configuration and keeps the configuration in one place
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            "email": "כתובת מייל",
            "first_name": "שם פרטי",
            "last_name": "שם משפחה",
        }
    

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="כתובת מייל")
    first_name = forms.CharField(required=True, label="שם פרטי")
    last_name = forms.CharField(required=True, label="שם משפחה")
    # nested namespace for configuration and keeps the configuration in one place
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            "email": "כתובת מייל",
            "first_name": "שם פרטי",
            "last_name": "שם משפחה",
        }

class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(required=False, label="תמונת פרופיל")
    
    
    class Meta:
        model = Profile
        fields = ['phone_number', 'image']
        labels = {
            "image": "תמונת פרופיל",
            "phone_number": "מספר נייד",
        }
