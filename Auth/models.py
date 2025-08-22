
from datetime import datetime  , timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from Roles.models import Role



class User(AbstractUser):
    user_timezone = models.CharField(max_length=50, default="UTC")
    roles = models.ManyToManyField(Role, related_name="users")
    active = models.BooleanField(default=True)
    frozen = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def has_permission(self, permission_code):
        return self.roles.filter(permissions__code=permission_code).exists()
