from django.urls import path
from django.conf.urls import url
from user.views import UserView, LoginView, VerifyUserView, PasswordRecoveryView

urlpatterns = [
    path('users/', UserView.as_view()),
    path('recovery-password/', PasswordRecoveryView.as_view()),
    url(r'^login/$', LoginView.as_view()),
    url(r'^users/verify/$', VerifyUserView.as_view()),
]
