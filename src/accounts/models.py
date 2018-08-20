from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    """
    email = models.EmailField(max_length=40, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    location = models.CharField(max_length=120, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    site = models.CharField(max_length=120, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return u'%s %s' % (self.first_name, self.last_name)

    def activate(self):
        """
        Activate user
        """
        self.is_active = True
        self.save()
        return self.is_active

    def send_activation_email(self):
        token_generator = PasswordResetTokenGenerator()
        activation_key = token_generator.make_token(self)
        activation_link = 'http://127.0.0.1:8000%s' % reverse('activation_link', kwargs={
            'token': activation_key,
            'pk': self.id
        })
        send_mail('email verified', activation_link, 'admin-api@co.com', [self.email], fail_silently=False)

    def __str__(self):
        return self.email
