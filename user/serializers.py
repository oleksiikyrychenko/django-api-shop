from rest_framework import serializers
from .models import Profile, Role


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role')

    def create(self, validated_data):
        return Profile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)

        instance.save()
        return instance


class RoleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'role_name')
