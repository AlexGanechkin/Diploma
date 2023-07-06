""" Набор представлений для CRUD-управления пользователями

RegistrationView - регистрация пользователя и создание записи в БД (любой пользователь)
LoginView - аутентификация пользователя по имени и паролю (доступно любому пользователю)
ProfileView - предоставление информации по аутентифицированному пользователою / ее обновление / выход пользователя
UpdatePasswordView - обновление пароля

"""

from typing import Any

from django.contrib.auth import get_user_model, login, logout
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response

from core.serializers import RegistrationSerializer, LoginSerializer, UserSerializer, UpdatePasswordSerializer

USER_MODEL = get_user_model()


class RegistrationView(generics.CreateAPIView):
    model = USER_MODEL
    permission_classes = [permissions.AllowAny]
    serializer_class = RegistrationSerializer


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """ Проверка данных пользователя с базой и авторизация пользователя """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request=request, user=user)
        return Response(serializer.data)


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = USER_MODEL.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs) -> Response:
        """ Закрытие сессии пользователя """

        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdatePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdatePasswordSerializer

    def get_object(self):
        return self.request.user
