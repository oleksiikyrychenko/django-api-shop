from rest_framework import serializers
from user.models import Profile, Role


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role_id')

    def create(self, validated_data):
        user = Profile.objects.create(**validated_data)
        user.set_password(user.password)
        user.confirmation_token = user.generate_confirmation_token(32)
        user.save()
        url = self.context['url'] + user.confirmation_token
        user.send_activation_email(url)
        return user

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
