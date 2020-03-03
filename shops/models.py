from django.db import models


class Shop(models.Model):
    owner = models.ForeignKey('user.Profile', related_name='user_profile', on_delete=models.CASCADE)
    country = models.CharField(max_length=100)
    title = models.CharField(max_length=100, default=None)
    street = models.CharField(max_length=100)
    house_number = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=120)
