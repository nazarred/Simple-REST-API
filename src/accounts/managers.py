from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email,and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_inactive_user(self, email, password=None, **extra_fields):
        extra_fields['is_active'] = False
        return self._create_user(email, password, **extra_fields)

    def create_user(self, email, password=None, **extra_fields):
        # extra_fields.setdefault('is_staff', False)
        # extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password=password, **extra_fields)