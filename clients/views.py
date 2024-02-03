from rest_framework import generics

from .models import Client
from .serializers import ClientSerializer


class ClientList(generics.ListCreateAPIView):
    """ Получение общего списка/добавление клиентов-держалетелей квизов """

    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class ClientDetail(generics.RetrieveUpdateDestroyAPIView):
    """ Получение, редактирование, удаление клиента-держателя квиза по его идентификатору """
    
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
