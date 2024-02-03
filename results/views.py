from rest_framework import viewsets

from backend.permissions import IsSuperuserOrReadOnly

from .models import Result
from .permissions import IsResultOwnerOrReadOnly
from .serializers import ResultSerializer


class ResultModelViewSet(viewsets.ModelViewSet):
    """ Вьюсэт для получение и редактирования инстансов модели результатов """
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsSuperuserOrReadOnly | IsResultOwnerOrReadOnly,]

    def get_queryset(self):
        quizz_id = self.request.query_params.get('quizz_id')
        if quizz_id:
            return Result.objects.filter(quizz_id=quizz_id)
        return super().get_queryset()
