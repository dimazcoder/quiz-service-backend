from rest_framework import generics

from .models import Attempter
from .serializers import AttempterSerializer


class AttempterList(generics.ListCreateAPIView):
    """Получение общего списка/добавление новых участников всех квизов"""

    queryset = Attempter.objects.all()
    serializer_class = AttempterSerializer


class AttempterDetail(generics.RetrieveUpdateDestroyAPIView):
    """Получение, редактирование, удаление участника по его идентификатору"""

    queryset = Attempter.objects.all()
    serializer_class = AttempterSerializer
