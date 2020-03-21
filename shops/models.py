from django.db import models


class Shop(models.Model):
    class Meta:
        db_table = 'shops'

    objects = models.Manager()

    owner = models.ForeignKey('user.Profile', related_name='user_profile', on_delete=models.CASCADE)
    country = models.CharField(max_length=100)
    title = models.CharField(max_length=100, default=None)
    street = models.CharField(max_length=100)
    house_number = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=120)

    def __str__(self):
        return self.title


class Category(models.Model):
    class Meta:
        db_table = 'categories'

    objects = models.Manager()

    left_key = models.IntegerField()
    right_key = models.IntegerField()
    title = models.CharField(max_length=200)
    depth = models.IntegerField()

    def __str__(self):
        return self.title


class Product(models.Model):
    class Meta:
        db_table = 'products'

    objects = models.Manager()

    owner = models.ForeignKey('user.Profile', related_name='product_owner', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default=None)
    category = models.ForeignKey('shops.Category', related_name='product_category', on_delete=models.CASCADE)
    price = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.title
