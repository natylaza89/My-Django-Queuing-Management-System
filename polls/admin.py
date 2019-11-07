from django.contrib import admin
from .models import Question, Choice

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'publish_date'] #, 'unique_user_votes'

class ChoiseAdmin(admin.ModelAdmin):
    list_display = ['question', 'choice_text', 'votes'] #, 'user_list_votes'

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiseAdmin)