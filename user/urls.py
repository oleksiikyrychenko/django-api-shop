from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserView.as_view({
        'get': 'list',
        'post': 'create',
        'put':'update',
        'delete':'delete',
    })),
]
