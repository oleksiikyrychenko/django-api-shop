from rest_framework import serializers
from .models import Shop, Category, Product, ProductsImages, FavoritesProducts
from user.serializers import UserSerializers
from drf_extra_fields.fields import Base64ImageField


class ShopSerializers(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"

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
    has_children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'left_key', 'right_key', 'title', 'depth', 'has_children')

    def create(self, validated_data):
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.left_key = validated_data.get('left_key', instance.left_key)
        instance.right_key = validated_data.get('right_key', instance.right_key)
        instance.title = validated_data.get('title', instance.title)
        instance.depth = validated_data.get('depth', instance.depth)

        instance.save()
        return instance

    def get_has_children(self, obj):
        categories = Category.objects.all()
        children = categories.filter(left_key__gt=obj.left_key, right_key__lt=obj.right_key)
        return children.count() > 0


class ProductsImagesSerializers(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = ProductsImages
        fields = "__all__"

    def create(self, validated_data):
        image = validated_data.pop('image')
        product = validated_data.pop('product')
        return ProductsImages.objects.create(image=image, product=product)

    def get_size(self, obj):
        file_size = ''
        if obj.image and hasattr(obj.image, 'size'):
            file_size = obj.image.size
        return file_size

    def get_name(self, obj):
        file_name = ''
        if obj.image and hasattr(obj.image, 'name'):
            file_name = obj.image.name
        return file_name

    def get_mime_type(self, obj):
        filename = obj.image.name
        return filename.split('.')[-1]


class ProductsSerializers(serializers.ModelSerializer):
    owner = UserSerializers(read_only=True)
    owner_id = serializers.IntegerField(write_only=True)
    category = CategorySerializers(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    product_images = ProductsImagesSerializers(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
        'id', 'title', 'price', 'description', 'owner', 'owner_id', 'category', 'category_id', 'product_images')

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.price = validated_data.get('price', instance.price)
        instance.description = validated_data.get('description', instance.description)

        instance.save()
        return instance


class FavoritesProductsSerializers(serializers.ModelSerializer):
    user = UserSerializers(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    product = ProductsSerializers(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FavoritesProducts
        fields = "__all__"

    def create(self, validated_data):
        return FavoritesProducts.objects.create(**validated_data)
