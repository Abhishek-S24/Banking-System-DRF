from django.db import models
from django.utils import timezone

from rest_framework import serializers

class UserPermission(models.Model):
    code = models.CharField(max_length=50, unique=True , primary_key=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

class UserRole(models.Model):
    name = models.CharField(max_length=50, unique=True, primary_key=True)
    user_permissions = models.ManyToManyField(UserPermission, related_name="user_roles")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if UserRole.objects.filter(name__iexact=self.name).exists():
            from django.core.exceptions import ValidationError
            raise ValidationError("Role with this name already exists.")

    def __str__(self):
        return self.name
