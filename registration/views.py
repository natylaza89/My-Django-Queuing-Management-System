from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.views import PasswordResetView
from .form import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.urls import reverse_lazy
from django.shortcuts import reverse, resolve_url

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from nails_project.settings import DEFAULT_FROM_EMAIL


class MyPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset.html"

    def post(self, request, *args, **kwargs):
        subject_template_name = 'registration/password_reset_subject.txt'
        email_template_name = 'registration/password_reset_email.html'

        requested_user = User.objects.get(email=request.POST['email'])

        context = {
            'request': request,
            'protocol': request.scheme,
            'user': requested_user,
            'domain': request.META['HTTP_HOST'],
            'uid': urlsafe_base64_encode(force_bytes(requested_user.pk)),
            'token': default_token_generator.make_token(requested_user)
        }

        html_loader = get_template(email_template_name)
        html_content = html_loader.render(context)
        subject = render_to_string(subject_template_name)
        subject = ''.join(subject.splitlines())
        message = EmailMultiAlternatives(subject, '', DEFAULT_FROM_EMAIL, [requested_user.email])
        message.attach_alternative(html_content, "text/html")
        message.send()

        return redirect('password_reset_done')      


def register(request):
    if request.method == 'POST':
        #form = UserRegisterForm(request.POST)

        user_form =  UserRegisterForm(request.POST)
        profile_form = ProfileUpdateForm(request.POST)#, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            email = user_form.cleaned_data.get('email')
            
            try:
                is_email_exist_in_db = User.objects.get(email=email)
            except User.DoesNotExist:
                is_email_exist_in_db = False

            if is_email_exist_in_db is False:
                user_form.save()
                
                profile_form.instance = user_form.instance.profile
                profile_form.instance.phone_number = profile_form.cleaned_data.get('phone_number')

                profile_form.save()
                messages.success(request, 'הפרופיל נוצר! ניתן כעת להתחבר לאתר.')

                return redirect('login')
            else:
                messages.error(request, 'האימייל כבר נמצא במערכת, אנא נסה שנית!')
    else:
        user_form = UserRegisterForm()
        profile_form = ProfileUpdateForm()

    return render(request, 'registration/register.html', {'user_form': user_form, 'profile_form':profile_form})

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'הפרופיל עודכן בהצלחה!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = { 
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'registration/profile.html', context)