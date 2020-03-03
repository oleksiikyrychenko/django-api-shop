import jwt
from django.contrib.auth import user_logged_in
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.serializers import jwt_payload_handler

from shop_api import settings
from .models import Role, Profile
from .serializers import UserSerializers, RoleSerializers
from django.contrib.auth import authenticate


class UserView(APIView):
    @permission_classes([IsAuthenticated, ])
    def get(self, request):
        users = Profile.objects.all()
        serializer = UserSerializers(users, many=True)
        return Response({"users": serializer.data})

    @permission_classes([AllowAny, ])
    def post(self, request):
        user = request.data.get('user')
        role = get_object_or_404(Role.objects.all(), role_name=user['role'])
        user['role_id'] = role.pk
        serializer = UserSerializers(data=user)

        if serializer.is_valid(raise_exception=True):
            user_saved = serializer.save()
            user_saved.set_password(user_saved.password)
            user_saved.save()
        return Response({"user": serializer.data})

    @permission_classes([IsAuthenticated, ])
    def put(self, request):
        pk = request.query_params.get('pk')
        user = get_object_or_404(Profile.objects.all(), pk=pk)
        data = request.data.get('user')
        serializer = UserSerializers(instance=user, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"user": serializer.data})

    @permission_classes([IsAuthenticated, ])
    def delete(self, request):
        pk = request.query_params.get('pk')
        user = get_object_or_404(Profile.objects.all(), pk=pk)
        user.delete()
        return Response({"message": "User has been deleted."})


class LoginView(APIView):
    @permission_classes([AllowAny, ])
    def post(self, request):
        if 'email' in request.data and 'password' in request.data:
            user = authenticate(username=request.data['email'], password=request.data['password'])
            try:
                payload = jwt_payload_handler(user)
                token = jwt.encode(payload, settings.SECRET_KEY)
                user_details = {
                    'token': token,
                    'user': model_to_dict(user)
                }
                user_logged_in.send(sender=user.__class__, request=request, user=user)
                return Response(user_details, status=status.HTTP_200_OK)

            except Exception as e:
                raise e
        else:
            return Response('Wrong credentials', status=status.HTTP_400_BAD_REQUEST)


class RoleView(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
