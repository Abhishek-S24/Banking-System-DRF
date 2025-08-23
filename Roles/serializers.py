from rest_framework import serializers
from .models import UserRole, UserPermission

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermission
        fields = ["code", "description"]

class RoleSerializer(serializers.ModelSerializer):
    user_permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=UserPermission.objects.all(),
        write_only=True,
        source="user_permissions" 
    )

    class Meta:
        model = UserRole
        fields = ["name", "user_permissions", "permission_ids"]

    def create(self, validated_data):
        permissions = validated_data.pop("user_permissions", [])
        role = UserRole.objects.create(**validated_data)
        role.user_permissions.set(permissions)  # assign M2M properly
        return role

    def update(self, instance, validated_data):
        permissions = validated_data.pop("user_permissions", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permissions is not None:
            instance.user_permissions.set(permissions)
        return instance