from django.contrib.auth import views
from django.urls import include, path, reverse_lazy

from users.views import SignUp

app_name = '%(app_label)s'

passwords = [
    path(
        'change/form/',
        views.PasswordChangeView.as_view(
            success_url=reverse_lazy('users:password_change_done'),
            template_name='users/password_change.html',
        ),
        name='password_change_form',
    ),
    path(
        'change/done/',
        views.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html',
        ),
        name='password_change_done',
    ),
    path(
        'reset/form/',
        views.PasswordResetView.as_view(
            success_url=reverse_lazy('users:password_reset_done'),
            template_name='users/password_reset_form.html',
        ),
        name='password_reset_form',
    ),
    path(
        'reset/complete/',
        views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
    path(
        'reset/done/',
        views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        views.PasswordResetConfirmView.as_view(
            success_url=reverse_lazy('users:password_reset_complete'),
            template_name='users/password_reset_confirm.html',
        ),
        name='password_reset_confirm',
    ),
]

urlpatterns = [
    path(
        'logout/',
        views.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout',
    ),
    path(
        'signup/',
        SignUp.as_view(),
        name='signup',
    ),
    path(
        'login/',
        views.LoginView.as_view(template_name='users/login.html'),
        name='login',
    ),
    path('password/', include(passwords)),
]
