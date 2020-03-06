from rest_framework import serializers
from .models import Shop, Category


class ShopSerializers(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['__all__']

    def create(self, validated_data):
        return Shop.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.country = validated_data.get('country', instance.country)
        instance.title = validated_data.get('title', instance.title)
        instance.street = validated_data.get('street', instance.street)
        instance.house_number = validated_data.get('house_number', instance.house_number)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)

        instance.save()
        return instance


class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'left_key', 'right_key', 'title', 'depth')

    def create(self, validated_data):
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.left_key = validated_data.get('left_key', instance.left_key)
        instance.right_key = validated_data.get('right_key', instance.right_key)
        instance.title = validated_data.get('title', instance.title)
        instance.depth = validated_data.get('depth', instance.depth)

        instance.save()
        return instance
