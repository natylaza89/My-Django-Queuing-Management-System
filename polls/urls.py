from django.contrib import admin
from django.urls import path, include

from . import views

#namespace polls
app_name = 'polls'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.QuestionDetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.QuestionResultDetailView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]