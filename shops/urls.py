from django.urls import path
from shops.views import ShopView, CategoryView, ProductsView, ProductImagesView

urlpatterns = [
    path('shop/', ShopView.as_view()),
    path('product/', ProductsView.as_view()),
    path('category/', CategoryView.as_view()),
    path('images/', ProductImagesView.as_view())
]
