from rest_framework import serializers
from .models import Profile, Role


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'password', 'username', 'first_name', 'last_name', 'email', 'role')


class RoleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'role_name')
