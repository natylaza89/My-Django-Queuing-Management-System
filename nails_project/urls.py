"""nails_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf.urls import url
from registration import views as users_views


urlpatterns = [
    path('admin/', admin.site.urls , name='admin'),
    path('register/', users_views.register, name='register'),
    path('profile/', users_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    # path('password-reset/',
        # auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'),
        # name='password_reset'),
    url('^password_reset/$', users_views.MyPasswordResetView.as_view(),
    #url('^password_reset/$', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'),
        # {
        # #'template_name': 'registration/reset_password.html',
        # #'email_template_name': 'email/password_reset/password_reset.txt',
        # 'html_email_template_name': 'registration/password_reset_email.html',
        # 'subject_template_name': 'registration/password_reset_subject.txt'
        # },
        name='password_reset'),
    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
        name='password_reset_confirm'),
    # url(r'^password-reset-confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
    #      auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
    #     name='password_reset_confirm'),
    path('password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'),
    path('', include('blog.urls')),
    path('polls/', include('polls.urls')),
    path('', include('calendarapp.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
