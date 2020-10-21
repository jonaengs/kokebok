import uuid as uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import PermissionsMixin

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(_('email address'), unique=True)  # Remember to validate forms in addition
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=256, blank=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    objects = CustomUserManager()

    def get_full_name(self):
        return self.name

    def __str__(self):
        return self.email
