from django.db import models
from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):
    class Meta:
        db_table = 'users'

    role_id = models.IntegerField()
    email = models.CharField(max_length=100, unique=True)
    confirmed_at = models.DateField(null=True, default=None)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'role']


class Role(models.Model):
    class Meta:
        db_table = 'roles'

    objects = models.Manager()

    role_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.role_name
