from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.ShopView.as_view())
]
