from .models import Question 

def add_variable_to_context(request):
     latest_poll = Question.objects.all().first()
     context = {'latest_poll': latest_poll}

     return context
    