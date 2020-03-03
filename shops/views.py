from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from shops.models import Shop
from shops.serializers import ShopSerializers
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
