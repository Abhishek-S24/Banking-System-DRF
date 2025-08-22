from rest_framework import serializers
from .models import User, Role

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Role.objects.all()
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "timezone",
            "roles",
            "active",
            "frozen",
            "password"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        roles = validated_data.pop("roles", [])
        password = validated_data.pop("password", None)
        user = User(**validated_data)

        if password:
            user.set_password(password)  # hash password properly
        user.save()

        if roles:
            user.roles.set(roles)  # assign roles after save

        return user

    def update(self, instance, validated_data):
        roles = validated_data.pop("roles", None)
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if roles is not None:
            instance.roles.set(roles)

        return instance
