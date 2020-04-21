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
from user.models import Role, Profile
from user.serializers import UserSerializers, RoleSerializers
from django.contrib.auth import authenticate
from datetime import datetime


class UserView(APIView):
    serializer_class = UserSerializers

    @permission_classes([IsAuthenticated, ])
    def get(self, request):
        pk = request.query_params.get('pk')
        if pk == 'me':
            users = request.user
            return Response({"user": model_to_dict(users)}, status=status.HTTP_200_OK)

        return Response({"user": {}}, status=status.HTTP_200_OK)

    @permission_classes([AllowAny, ])
    def post(self, request):
        user = request.data.get('user')
        role = get_object_or_404(Role.objects.all(), role_name=user['role'])
        user['role_id'] = role.pk
        url = request.build_absolute_uri('verify/?token=')
        serializer = self.serializer_class(data=user, context={'url': url})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"user": serializer.data}, status=status.HTTP_201_CREATED)

    @permission_classes([IsAuthenticated, ])
    def put(self, request):
        pk = request.query_params.get('pk')
        user = get_object_or_404(Profile.objects.all(), pk=pk)
        data = request.data.get('user')
        serializer = self.serializer_class(instance=user, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)

    @permission_classes([IsAuthenticated, ])
    def delete(self, request):
        pk = request.query_params.get('pk')
        user = get_object_or_404(Profile.objects.all(), pk=pk)
        user.delete()
        return Response({"message": "User has been deleted."}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if 'email' in request.data and 'password' in request.data:
            user = get_object_or_404(Profile.objects.all(), email=request.data['email'])
            if user.confirmed_at is None:
                return Response('Please activate your account', status=status.HTTP_400_BAD_REQUEST)

            auth_user = authenticate(username=request.data['email'], password=request.data['password'])
            try:
                payload = jwt_payload_handler(auth_user)
                token = jwt.encode(payload, settings.SECRET_KEY)
                user_details = {
                    'token': token,
                    'user': model_to_dict(auth_user)
                }
                user_logged_in.send(sender=auth_user.__class__, request=request, user=auth_user)
                return Response(user_details, status=status.HTTP_200_OK)

            except Exception as e:
                raise e
        else:
            return Response('Wrong credentials', status=status.HTTP_400_BAD_REQUEST)


class VerifyUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        confirmation_token = request.query_params.get('token')
        if not confirmation_token:
            return Response('token is required', status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(Profile.objects.all(), confirmation_token=confirmation_token)
        user.confirmation_token = None
        user.is_active = True
        user.confirmed_at = datetime.now()
        user.save()

        return Response('User was successful verified', status=status.HTTP_200_OK)


class PasswordRecoveryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get('token')
        if token:
            get_object_or_404(Profile.objects.all(), confirmation_token=token)
            return Response('Code is correct', status=status.HTTP_200_OK)
        return Response('Token is required', status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        password = request.data.get('password')
        code = request.data.get('code')
        user = get_object_or_404(Profile.objects.all(), confirmation_token=code)
        user.set_password(password)
        user.confirmation_token = None
        user.save()

        return Response('Password was successful changed', status=status.HTTP_200_OK)

    def delete(self, request):
        if 'email' in request.data:
            user = get_object_or_404(Profile.objects.all(), email=request.data['email'])
            user.confirmation_token = user.generate_confirmation_token(32)
            user.send_password_recovery()
            user.save()

            return Response('Password recovered', status=status.HTTP_200_OK)

        return Response('Email is required field', status=status.HTTP_400_BAD_REQUEST)


class RoleView(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
