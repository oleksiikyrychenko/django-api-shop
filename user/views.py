from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Role, Profile
from .serializers import UserSerializers, RoleSerializers


class UserView(APIView):
    def get(self, request):
        users = Profile.objects.all()
        serializer = UserSerializers(users, many=True)
        return Response({"users": serializer.data})

    def post(self, request):
        user = request.data.get('user')
        serializer = UserSerializers(data=user)

        if serializer.is_valid(raise_exception=True):
            user_saved = serializer.save()
            user_saved.set_password(user_saved.password)
            user_saved.save()
        return Response({"user": serializer.data})

    def put(self, request, pk):
        user = get_object_or_404(Profile.objects.all(), pk=pk)
        data = request.data.get('user')
        serializer = UserSerializers(instance=user, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"user": serializer.data})

    def delete(self, request, pk):
        article = get_object_or_404(Profile.objects.all(), pk=pk)
        article.delete()
        return Response({"message": "User has been deleted."})


class RoleView(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
