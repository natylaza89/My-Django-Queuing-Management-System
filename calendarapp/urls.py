from django.contrib import admin
from django.urls import path, include, reverse
from django.conf.urls import url

from . import views

#namespace polls
app_name = 'calendar'

# urlpatterns = [
#     path('', views.CalendarView.as_view(), name='calendar'),
#     path('', views.new_treatment, name='calendar-new-treatment'),
# ]
urlpatterns = [
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('calendar/my-treatments/', views.CalendarMyTreatmentsView.as_view(), name='calendar_my_treatments'),
    path('calendar/new/', views.treatment, name='calendar_new_treatment'),
    path('calendar/date_view/<treatment_date>/', views.day_treatment, name='calendar_treatment_day_view'),
    path('calendar/edit/treatment/<treatment_id>/', views.treatment, name='calendar_edit_treatment'),
    #path('calendar/treatment/delete/<treatment_id>/', views.delete_treatment, name='calendar_treatment_delete'),
    path('calendar/treatment/delete/<int:pk>/', views.TreatmentDeleteView.as_view(), name='calendar_treatment_delete'),
    #url(r'^calendar/delete/treatment/(?P<treatment_id>.*)', views.delete_treatment, name='calendar_treatment_delete'),
    #path(r'^calendar/treatment/delete/<int:pk>/$', views.TreatmentDeleteView.as_view(), name='calendar_treatment_delete'),
    #url(r'^calendar/treatment/delete/(?P<pk>\d+)/$', views.TreatmentDeleteView.as_view(), name='calendar_treatment_delete'),
    #url(r'^event/new/$', views.event, name='event_new'),
    #path('calendar/treatment/<treatment_id>/delete/', views.TreatmentDeleteView.as_view(), name='calendar_treatment_delete'),
    #url(r'^calendar/$', views.CalendarView.as_view(), name='calendar'),
    #url(r'^event/new/$', views.event, name='event_new'),
]