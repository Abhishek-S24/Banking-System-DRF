
from datetime import datetime  , timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from Roles.models import UserRole



class User(AbstractUser):
    user_timezone = models.CharField(max_length=50, default="UTC")
    roles = models.ManyToManyField(UserRole, related_name="custom_user_roles")
    active = models.BooleanField(default=True)
    frozen = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def has_permission(self, permission_code):
        return self.roles.filter(user_permissions__code=permission_code).exists()
