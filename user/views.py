from rest_framework import viewsets
from rest_framework.response import Response

from .models import Role
from .serializers import UserSerializers, RoleSerializers


class UserView(viewsets.ViewSet):
    serializer_class = UserSerializers

    def list(self, request):
        return Response('list')

    def create(self, request):
        return Response('create')

    def update(self, request):
        return Response('update')

    def delete(self, request):
        return Response('delete')


class RoleView(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
