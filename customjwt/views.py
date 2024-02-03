from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """ Кастомный вью для переопределения сериализатора для генерации JWT """
    serializer_class = CustomTokenObtainPairSerializer
    