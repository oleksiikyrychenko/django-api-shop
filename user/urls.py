from django.urls import path
from django.conf.urls import url
from user.views import UserView, LoginView

urlpatterns = [
    path('users/', UserView.as_view()),
    url(r'^login/$', LoginView.as_view()),
]
