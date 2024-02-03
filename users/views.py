from django.contrib.auth import get_user_model
from rest_framework import viewsets

User = get_user_model()

from .serializers import UserReadSerializer, UserCreateSerializer


class UserModelViewSet(viewsets.ModelViewSet):
    """ Вьюсэт для работы с моделью пользователей (пока только получение) """
    queryset = User.objects.all()
    serializer_class = UserReadSerializer

    def get_serializer_class(self):
        if self.request.method in ['POST']:
            return UserCreateSerializer
        return super().get_serializer_class()
