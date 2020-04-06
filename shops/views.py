from django.forms import model_to_dict
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from shops.models import Shop, Category, Product, ProductsImages, FavoritesProducts
from shops.serializers import ShopSerializers, CategorySerializers, ProductsSerializers, ProductsImagesSerializers, FavoritesProductsSerializers
from django.shortcuts import get_object_or_404


class ShopView(APIView):
    @permission_classes([IsAuthenticated, ])
    def get(self, request):
        shops = Shop.objects.all()
        serializer = ShopSerializers(shops, many=True)
        return Response({"data": serializer.data})

    @permission_classes([IsAuthenticated, ])
    def post(self, request):
        data = request.data.get('data')
        serializer = ShopSerializers(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"data": serializer.data})

    @permission_classes([IsAuthenticated, ])
    def put(self, request):
        pk = request.query_params.get('pk')
        shop = get_object_or_404(Shop.objects.all(), pk=pk)
        data = request.data.get('data')
        serializer = ShopSerializers(instance=shop, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"data": serializer.data})

    @permission_classes([IsAuthenticated, ])
    def delete(self, request):
        pk = request.query_params.get('pk')
        shop = get_object_or_404(Shop.objects.all(), pk=pk)
        shop.delete()
        return Response({"message": "Shop has been deleted."})


class CategoryView(APIView):
    @permission_classes([AllowAny, ])
    def get(self, request):
        pk = request.query_params.get('pk')
        categories = Category.objects.all()
        if pk:
            category = get_object_or_404(Category.objects.all(), pk=pk)
            children_categories = categories.filter(left_key__gt=category.left_key, right_key__lt=category.right_key)
            serializer = CategorySerializers(children_categories, many=True)
            return Response({"data": serializer.data})

        root_categories = Category.objects.all().filter(depth=0)
        serializer = CategorySerializers(root_categories, many=True)
        return Response({"data": serializer.data})

    @permission_classes([AllowAny, ])
    def post(self, request):
        title = request.data.get('title')
        parent_category_id = request.data.get('parent_category_id')
        all_categories = Category.objects.all()

        if all_categories.count() == 0:
            data = {
                'left_key': 1,
                'right_key': 2,
                'title': title,
                'depth': 0
            }
            return self.save_data(data)

        if parent_category_id == 0:
            categories = all_categories.order_by('-right_key')
            latest_category = categories[0]
            data = {
                'left_key': latest_category.right_key + 1,
                'right_key': latest_category.right_key + 2,
                'title': title,
                'depth': 0
            }
            return self.save_data(data)

        parent_category = get_object_or_404(all_categories, pk=parent_category_id)
        categories_other_branch = all_categories.filter(left_key__gt=parent_category.right_key)

        for category in categories_other_branch:
            category.right_key = category.right_key + 2
            category.left_key = category.left_key + 2
            category.save()

        categories_parent_branch = all_categories.filter(right_key__gte=parent_category.right_key,
                                                         left_key__lt=parent_category.right_key)

        for category in categories_parent_branch:
            category.right_key = category.right_key + 2
            category.save()

        data = {
            'left_key': parent_category.right_key,
            'right_key': parent_category.right_key + 1,
            'title': title,
            'depth': parent_category.depth + 1
        }

        return self.save_data(data)

    @permission_classes([AllowAny, ])
    def put(self, request):
        pk = request.query_params.get('pk')
        title = request.data.get('title')
        category = get_object_or_404(Category.objects.all(), pk=pk)
        category.title = title
        category.save()

        return Response({'data': model_to_dict(category)})

    @permission_classes([AllowAny, ])
    def delete(self, request):
        pk = request.query_params.get('pk')
        category = get_object_or_404(Category.objects.all(), pk=pk)
        category_for_delete = Category.objects.filter(left_key__gte=category.left_key,
                                                      right_key__lte=category.right_key)
        for category in category_for_delete:
            category.delete()

        parent_category = Category.objects.filter(right_key__gt=category.right_key, left_key__lt=category.left_key)
        for category in parent_category:
            category.right_key = category.right_key - (category.right_key - category.left_key + 1)
            category.save()

        rest_categories = Category.objects.filter(left_key__gt=category.right_key)
        for category in rest_categories:
            category.left_key = category.left_key - (category.right_key - category.left_key + 1)
            category.save()

        return Response({"data": "delete"})

    def save_data(self, data):
        serializer = CategorySerializers(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"data": serializer.data})


class ProductsView(APIView):
    @permission_classes([IsAuthenticated, ])
    def get(self, request):
        pk = request.query_params.get('pk')
        if not pk:
            serializer = ProductsSerializers(Product.objects.all(), many=True)
            return Response({"data": serializer.data})

        product = get_object_or_404(Product.objects.all(), pk=pk)
        return Response({"data": ProductsSerializers(product).data})

    @permission_classes([AllowAny, ])
    def post(self, request):
        data = request.data
        files = request.data.get('files')
        if 'files' in data:
            del data['files']
        products_serializer = ProductsSerializers(data=data)
        if products_serializer.is_valid(raise_exception=True):
            products_serializer.save()

        for file in files:
            data = {
                'image': file,
                'product': products_serializer.data['id']
            }
            serializer = ProductsImagesSerializers(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

        return Response({"data": products_serializer.data})

    @permission_classes([IsAuthenticated, ])
    def put(self, request):
        pk = request.query_params.get('pk')
        product = get_object_or_404(Product.objects.all(), pk=pk)
        data = request.data.get('data')
        serializer = ProductsSerializers(instance=product, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"data": serializer.data})

    @permission_classes([IsAuthenticated, ])
    def delete(self, request):
        pk = request.query_params.get('pk')
        product = get_object_or_404(Product.objects.all(), pk=pk)
        product.delete()
        return Response({"message": "Product has been deleted."})


class ProductImagesView(APIView):
    @permission_classes([AllowAny, ])
    def get(self, request):
        images = ProductsImages.objects.all()
        serializer = ProductsImagesSerializers(images, many=True)
        return Response({"data": serializer.data})


class FavoritesProductsView(APIView):
    @permission_classes([AllowAny, ])
    def get(self, request):
        pk = request.query_params.get('user_id')
        favorite_product = FavoritesProducts.objects.all().filter(user_id=pk)
        serializer = FavoritesProductsSerializers(favorite_product, many=True)
        return Response({"data": serializer.data})

    @permission_classes([AllowAny, ])
    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        data = {
            'user_id': user_id,
            'product_id': product_id
        }
        serializer = FavoritesProductsSerializers(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"data": serializer.data})

    @permission_classes([AllowAny, ])
    def delete(self, request):
        pk = request.query_params.get('pk')
        favorite_product = get_object_or_404(FavoritesProducts.objects.all(), pk=pk)
        favorite_product.delete()
        return Response({"message": "Product was successful deleted from favorites"})
