from rest_framework import serializers
from .models import Shop


class ShopSerializers(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['__all__']

    def create(self, validated_data):
        return Shop.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.country = validated_data.get('username', instance.country)
        instance.title = validated_data.get('first_name', instance.title)
        instance.street = validated_data.get('last_name', instance.street)
        instance.house_number = validated_data.get('email', instance.house_number)
        instance.phone = validated_data.get('email', instance.phone)
        instance.email = validated_data.get('email', instance.email)

        instance.save()
        return instance
