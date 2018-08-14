from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin
)

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    """
    email = models.EmailField(max_length=40, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    activation_key = models.CharField(max_length=40, blank=True)

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

    def activate(self, activation_key):
        """
        Validate an activation key and activate user if valid.
        """
        if self.activation_key == activation_key:
            self.is_active = True
            self.save()
        return self.is_active

    def __str__(self):
        return self.email
