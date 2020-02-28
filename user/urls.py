from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('users/', views.UserView.as_view()),
    url(r'^login/$', views.LoginView.as_view()),
]
