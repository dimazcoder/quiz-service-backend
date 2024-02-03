from rest_framework import viewsets

from backend.permissions import IsSuperuserOrReadOnly

from .models import Question
from .permissions import IsQuestionOwnerOrReadOnly
from .serializers import (QuestionCreateSerializer, QuestionSerializer,
                          QuestionUpdateSerializer)


class QuestionModelViewSet(viewsets.ModelViewSet):
    """ Вьюсэт для получение и редактирования инстансов модели вопросов """
    queryset = Question.objects.all()
    permission_classes = [IsSuperuserOrReadOnly | IsQuestionOwnerOrReadOnly]

    def get_queryset(self):
        quizz_id = self.request.query_params.get('quizz_id')
        if quizz_id:
            quizz_questions = Question.objects.filter(quizz_id=quizz_id)
            return quizz_questions

        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method in ['POST']:
            return QuestionCreateSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return QuestionUpdateSerializer
        else:
            return QuestionSerializer
        