from django.http import JsonResponse
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.status import HTTP_200_OK

from backend.permissions import IsSuperuserOrReadOnly

from .models import Variant, VariantsGraph
from .serializers import (VariantSerializer,
                          VariantsGraphCreateOrUpdateSerializer)
from .services import get_graph_for_variant


class VariantList(generics.ListCreateAPIView):
    """ Получение общего списка/добавление вариантов ответа """

    queryset = Variant.objects.all()
    serializer_class = VariantSerializer

class VariantDetail(generics.RetrieveUpdateDestroyAPIView):
    """ Получение, редактирование, удаление варианта ответа по его идентификатору """

    queryset = Variant.objects.all()
    serializer_class = VariantSerializer

class VariantsGraphModelViewSet(viewsets.ModelViewSet):
    """ Вьюсет для сохранения/обновления графов вариантов ответа """
    queryset = VariantsGraph.objects.all()
    permission_classes = [IsSuperuserOrReadOnly]

    @action(detail=False)
    def create_or_update(self, request):
        serialized_graphs_data = VariantsGraphCreateOrUpdateSerializer(data=request.data, many=True)
        if serialized_graphs_data.is_valid():
            graphs_to_create = []
            graphs_to_update = []

            for serialized_graph_data in serialized_graphs_data.validated_data:
                graph = get_graph_for_variant(variant_id=serialized_graph_data['variant'].id) if serialized_graph_data['variant'].id else None

                if graph:
                    graph.result = serialized_graph_data['result']
                    graph.next_question = serialized_graph_data['next_question']
                    graph.modified_user = request.user
                    graphs_to_update.append(graph)
                else:
                    graphs_to_create.append(VariantsGraph(**serialized_graph_data, created_user=request.user, modified_user=request.user))

            if graphs_to_update:
                VariantsGraph.objects.bulk_update(graphs_to_update, ['result_id', 'next_question_id', 'modified_user_id'])

            if graphs_to_create:
                VariantsGraph.objects.bulk_create(graphs_to_create)
  
        return JsonResponse({'message': 'Графы успешно сохранены!'}, status=HTTP_200_OK)
