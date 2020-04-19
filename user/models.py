from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from shop_api.settings import SENDGRID_API_KEY, SEND_FROM_MAIL


class Profile(AbstractUser):
    class Meta:
        db_table = 'users'

    role_id = models.IntegerField()
    email = models.CharField(max_length=100, unique=True)
    confirmed_at = models.DateField(null=True, default=None)
    confirmation_token = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'role']

    def generate_confirmation_token(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def send_activation_email(self, url):
        message = Mail(
            from_email=SEND_FROM_MAIL,
            to_emails=self.email,
            subject='Active you account, please!',
            html_content='<strong>Go to this page and confirm you email.</strong> <a href=' + url + '>Activate</a>'
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        return sg.send(message)

    def send_password_recovery(self):
        code = self.confirmation_token
        message = Mail(
            from_email=SEND_FROM_MAIL,
            to_emails=self.email,
            subject='Password recovery!',
            html_content='<strong>Your confirmation code:' + code + '</strong>'
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        return sg.send(message)


class Role(models.Model):
    class Meta:
        db_table = 'roles'

    objects = models.Manager()

    role_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.role_name
