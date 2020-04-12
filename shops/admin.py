from django.contrib import admin
from shops.models import Shop, Category, Product, ProductsImages, FavoritesProducts

admin.site.register(Shop)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductsImages)
admin.site.register(FavoritesProducts)
