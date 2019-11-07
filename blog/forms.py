from django import forms
from .models import Post

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True, label='מייל השולח')
    subject = forms.CharField(max_length=50, required=True, label='נושא ההודעה')
    message = forms.CharField(max_length=150, required=True, widget=forms.Textarea, label='תוכן ההודעה')

    class Meta:
        model: Post
        fields = ['from_email', 'subject', 'message']
        labels = {
            "from_email": "מייל השולח",
            "subject": "נושא",
            "message": "הודעה",
        }
