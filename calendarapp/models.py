from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Treatments(models.Model):
    TREATMENT_TYPE = (
        ('לק רגיל', 'לק רגיל'),
        ("לק ג'ל", "לק ג'ל"),
        ('לק ציורי', 'לק ציורי'),
    )
    TREATMENT_HOUR = (
        ('08:00', '08:00'),
        ('09:00', '09:00'),
        ('10:00', '10:00'),
        ('11:00', '11:00'),
        ('12:00', '12:00'),
        ('13:00', '13:00'),
        ('14:00', '14:00'),
        ('15:00', '15:00'),
        ('16:00', '16:00'),
        ('17:00', '17:00'),
        ('18:00', '18:00'),
        ('19:00', '19:00'),
)

    title = models.CharField(max_length=8, choices=TREATMENT_TYPE, default="לק ג'ל")
    description = models.TextField(max_length=50)
    date = models.DateField(null=True) 
    time = models.CharField(max_length=5, choices=TREATMENT_HOUR, default='8:00')#models.TimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=False)
    google_event_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title

    @property
    def get_html_url(self):
         url = reverse('calendar:calendar_edit_treatment', args=(self.id,))
         return f'{url}'
