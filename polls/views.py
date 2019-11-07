from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView

from blog.models import Post
from .models import Question, Choice
# Create your views here.


class IndexView(ListView):
    model = Question
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        # Return the last five published questions.
        return Question.objects.order_by('-publish_date')[:5]

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'polls/detail.html'

class QuestionResultDetailView(LoginRequiredMixin, DetailView):
    model = Question
    template_name = 'polls/results.html'
    

def index(request):
    latest_question_list = Question.objects.order_by('-publish_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

# def details(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})

# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/results.html', {'question': question})

def vote(request, question_id):
    posts = Post.objects.all()
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        # Always return an Htt
        result = render(request, 'blog/home.html', {
            'poll_error_message':"לא בחרת באף אופציה!",
            'posts': posts
        })
    else:
        if request.user.is_authenticated:
            user_list = [ str(username) for username in question.unique_user_votes.all() ]
            if str(request.user) not in user_list:
                selected_choice.votes += 1
                selected_choice.user_list_votes.add(request.user)
                question.unique_user_votes.add(request.user)
                selected_choice.save()
                question.save()
                result = HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
                # Always return an HttpResponseRedirect after successfully dealing
                # with POST data. This prevents data from being posted twice if a
                # user hits the Back button.
            else:
                result = render(request, 'blog/home.html', {
                            'poll_error_message': "הצבעת כבר! תודה! דעתך חשובה לנו!",
                            'posts': posts
                        })
        else:
                result = render(request, 'blog/home.html', {
                                'poll_error_message': "רק משתמשים מחוברים יכולים לראות את תוצאת הסקר!",
                                'posts': posts
                        })   
    finally:
        return result

        
