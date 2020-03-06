from django.urls import path
from shops.views import ShopView, CategoryView

urlpatterns = [
    path('shop/', ShopView.as_view()),
    path('category/', CategoryView.as_view())
]
