from django.forms import model_to_dict
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from shops.models import Shop, Category, Product, ProductsImages, FavoritesProducts
from shops.serializers import ShopSerializers, CategorySerializers, ProductsSerializers, ProductsImagesSerializers, \
    FavoritesProductsSerializers
from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework import generics
from django.db.models import F
from rest_framework import status
from shops.pagination import PaginationHandlerMixin


class ShopView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShopSerializers

    def get(self, request):
        shops = Shop.objects.all()
        serializer = self.serializer_class(shops, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.get('data')
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)

    def put(self, request):
        pk = request.query_params.get('pk')
        shop = get_object_or_404(Shop.objects.all(), pk=pk)
        data = request.data.get('data')
        serializer = self.serializer_class(instance=shop, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request):
        pk = request.query_params.get('pk')
        shop = get_object_or_404(Shop.objects.all(), pk=pk)
        shop.delete()
        return Response({"message": "Shop has been deleted."}, status=status.HTTP_200_OK)


class CategoryView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializers

    def get(self, request):
        pk = request.query_params.get('pk')
        categories = Category.objects.all()
        if pk:
            category = get_object_or_404(Category.objects.all(), pk=pk)
            children_categories = categories.filter(left_key__gt=category.left_key, right_key__lt=category.right_key)
            serializer = self.serializer_class(children_categories, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)

        root_categories = categories.filter(depth=0)
        serializer = self.serializer_class(root_categories, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

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
        # Update categories in other branches
        all_categories.filter(left_key__gt=parent_category.right_key) \
            .update(right_key=F('right_key') + 2, left_key=F('left_key') + 2)

        # Update categories in parent branch
        all_categories.filter(right_key__gte=parent_category.right_key,
                              left_key__lt=parent_category.right_key) \
            .update(right_key=F('right_key') + 2)

        data = {
            'left_key': parent_category.right_key,
            'right_key': parent_category.right_key + 1,
            'title': title,
            'depth': parent_category.depth + 1
        }

        return self.save_data(data)

    def put(self, request):
        pk = request.query_params.get('pk')
        title = request.data.get('title')
        category = get_object_or_404(Category.objects.all(), pk=pk)
        category.title = title
        category.save()

        return Response({'data': model_to_dict(category)}, status=status.HTTP_200_OK)

    def delete(self, request):
        pk = request.query_params.get('pk')
        current_category = get_object_or_404(Category.objects.all(), pk=pk)
        # Delete current category and it children
        Category.objects.filter(left_key__gte=current_category.left_key,
                                right_key__lte=current_category.right_key).delete()

        # Update parent branch
        Category.objects.filter(right_key__gt=current_category.right_key,
                                left_key__lt=current_category.left_key) \
            .update(right_key=F('right_key') - (current_category.right_key - current_category.left_key + 1))

        # Updates rest categories
        Category.objects.filter(left_key__gt=current_category.right_key) \
            .update(left_key=F('left_key') - (current_category.right_key - current_category.left_key + 1),
                    right_key=F('right_key') - (current_category.right_key - current_category.left_key + 1))

        return Response({"data": "delete"}, status=status.HTTP_200_OK)

    def save_data(self, data):
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)


class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class ProductsView(APIView, PaginationHandlerMixin):
    permission_classes = [AllowAny, ]
    serializer_class = ProductsSerializers
    pagination_class = BasicPagination

    def get(self, request):
        pk = request.query_params.get('pk')
        products = Product.objects.all()
        page = self.paginate_queryset(products)
        if pk:
            product = get_object_or_404(products, pk=pk)
            return Response({"data": self.serializer_class(product, context={'request': request}).data},
                            status=status.HTTP_200_OK)
        if page is not None:
            serializer = self.get_paginated_response(
                self.serializer_class(page, many=True, context={'request': request}).data)
        else:
            serializer = self.serializer_class(products, many=True, context={'request': request})

        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        files = request.data.get('files')
        if 'files' in data:
            del data['files']
        products_serializer = self.serializer_class(data=data, context={'request': request})
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

        return Response({"data": products_serializer.data}, status=status.HTTP_200_OK)

    def put(self, request):
        pk = request.query_params.get('pk')
        product = get_object_or_404(Product.objects.all(), pk=pk)
        data = request.data.get('data')
        serializer = self.serializer_class(instance=product, data=data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request):
        pk = request.query_params.get('pk')
        product = get_object_or_404(Product.objects.all(), pk=pk)
        product.delete()
        return Response({"message": "Product has been deleted."}, status=status.HTTP_200_OK)


class ProductSearchAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    search_fields = ['title']
    filter_backends = (filters.SearchFilter,)
    queryset = Product.objects.all()
    serializer_class = ProductsSerializers


class ProductImagesView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductsImagesSerializers

    def get(self, request):
        images = ProductsImages.objects.all()
        serializer = self.serializer_class(images, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


class FavoritesProductsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoritesProductsSerializers

    def get(self, request):
        pk = request.query_params.get('user_id')
        favorite_product = FavoritesProducts.objects.filter(user_id=pk)
        serializer = self.serializer_class(favorite_product, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        data = {
            'user_id': user_id,
            'product_id': product_id
        }
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request):
        pk = request.query_params.get('pk')
        favorite_product = get_object_or_404(FavoritesProducts.objects.all(), pk=pk)
        favorite_product.delete()
        return Response({"message": "Product was successful deleted from favorites"}, status=status.HTTP_200_OK)
