from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from questions.serializers import QuestionGraphSerializer
from questions.services import (
    get_question_for_quizz_by_id, get_questions_for_quizz,
    get_questions_with_varitants_without_graph_for_quizz,
    get_start_question_for_quizz)
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from results.serializers import ResultSerializer
from results.services import get_results_without_graph_for_quizz

from backend.permissions import (IsAuthenticatedOrOwnerOrReadOnly,
                                 IsSuperuserOrReadOnly)

from .models import (QUIZZ_STATUS_ACTIVE, QUIZZ_TYPE_QUEST, Quizz,
                     QuizzComplexity)
from .serializers import QuizzComplexitySerializer, QuizzSerializer


class QuizzModelViewSet(viewsets.ModelViewSet):
    """ Вьюсэт для получения и редактирование инстансов модели квизов """
    serializer_class = QuizzSerializer
    queryset = Quizz.objects.filter(status=QUIZZ_STATUS_ACTIVE)
    permission_classes = [IsSuperuserOrReadOnly | IsAuthenticatedOrOwnerOrReadOnly,]

    def get_object(self):
        alias = self.kwargs.get('alias', None)
        if alias:
            return get_object_or_404(Quizz, alias=alias) if self.request.user and self.request.user.is_superuser else get_object_or_404(Quizz, alias=alias, status=QUIZZ_STATUS_ACTIVE)
        return super(QuizzModelViewSet, self).get_object()
    
    def get_queryset(self):
        if self.request.user and self.request.user.is_superuser:
            return Quizz.objects.all()
        return super().get_queryset()
    
    @action(detail=False)
    def get_questionsgraph_list(self, request, pk=None):
        quizz = get_object_or_404(Quizz, id=pk, quizz_type=QUIZZ_TYPE_QUEST)
        questions = get_questions_for_quizz(quizz_id=quizz.id)
        
        serializer = QuestionGraphSerializer(questions, many=True)
        return JsonResponse(serializer.data, safe=False)
    
    @action(detail=False)
    def get_questionsgraph_detailed(self, request, pk=None, question_id=None):
        quizz = get_object_or_404(Quizz, id=pk, quizz_type=QUIZZ_TYPE_QUEST)
        
        if question_id:
            question = get_question_for_quizz_by_id(quizz_id=quizz.id, question_id=question_id)
        else:
            question = get_start_question_for_quizz(quizz_id=quizz.id)
            # question = Question.objects.values('id', 'text').filter(quizz_id=quizz.id, is_start=True).annotate(variants_count=Count('variants__id'), variants_with_graph_count=Count('variants__graph__id')).first()

        questions = get_questions_with_varitants_without_graph_for_quizz(quizz_id=quizz.id)
        questions_serializer = QuestionGraphSerializer(questions, many=True).data if questions else None

        results = get_results_without_graph_for_quizz(quizz_id=quizz.id)
        results_serializer = ResultSerializer(results, many=True).data if results else None
        
        question_serializer = QuestionGraphSerializer(question).data
        return JsonResponse({
            'question': question_serializer, 
            'questions_without_graphs': questions_serializer, 
            'results_without_graphs': results_serializer
        }, safe=False)

class QuizzComplexityList(generics.ListCreateAPIView):
    """ Получение общего списка/добавление сложности для квиза """

    queryset = QuizzComplexity.objects.all()
    serializer_class = QuizzComplexitySerializer

class QuizzComplexityDetail(generics.RetrieveUpdateDestroyAPIView):
    """ Получение, редактирование, удаление сложности для квиза по её идентификатору """

    queryset = QuizzComplexity.objects.all()
    serializer_class = QuizzComplexitySerializer
