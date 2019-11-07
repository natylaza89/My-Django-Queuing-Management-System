from django.contrib import admin
from .models import Treatments

class TreatmentsAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'date', 'time', 'google_event_id', 'user']


admin.site.register(Treatments, TreatmentsAdmin)