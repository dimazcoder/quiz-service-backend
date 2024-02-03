from typing import List

from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet
from questions.models import Question
from results.models import Result

from .models import Variant, VariantsGraph

User = get_user_model()

def check_variants_without_graph_for_quizz(quizz_id: int) -> bool:
    """ Проверяет наличие ваиантов к которым не привязан граф """
    return Variant.objects.filter(
        question_id__in=Question.objects.filter(quizz_id=quizz_id)
    ).filter(Q(graph__isnull=True) | (Q(graph__result_id=0) & Q(graph__next_question_id=0))).exists()

def get_variant_by_id(variant_id: int) -> Variant | None:
    """ Получение варианта по его идентификатору """
    try:
        return Variant.objects.get(pk=variant_id)
    except Variant.DoesNotExist:
        return None

def create_variant(
    text: str, 
    created_user: User, 
    question: Question, 
    results: List[Result] = [], 
    sort_order: int = 0, 
    text_selected: str = '', 
    complexity: int = 0) -> Variant:
    """ Создание варианта ответа """
    variant = Variant.objects.create(
        text=text, 
        created_user=created_user, 
        modified_user=created_user, 
        question=question, 
        sort_order=sort_order, 
        text_selected=text_selected, 
        complexity=complexity
    )
    
    if results:
        variant.results.set(results)

    return variant

def update_variant(variant: Variant, variant_data: dict, results: List[Result] = []) -> Variant:
    """ Обновление данных варианта по его идентификатору """
    for attr, value in variant_data.items():
        setattr(variant, attr, value)
    variant.save()

    if results:
        variant.results.set(results)
    
    return variant

def remove_variants_for_question(question_id: int) -> None:
    """ Удаляет варианты ответа по идентификатору вопроса """
    Variant.objects.filter(question_id=question_id).delete()

def get_variants_with_results_for_question(question_id: int) -> QuerySet[Variant]:
    """ Получение вариантов ответа на вопрос, к которым привязан результат """
    return Variant.objects.filter(question_id=question_id).exclude(results__isnull=True)

def remove_variant(variant_id: int) -> None:
    """ Удаляет вариант ответа по идентификатору """
    Variant.objects.filter(pk=variant_id).delete()

def get_variants_for_question(question_id: int) -> QuerySet[Variant]:
    """ Получение списка вариантов для вопроса """
    return Variant.objects.filter(question_id=question_id).select_related('graph')

def get_graph_for_variant(variant_id: int) -> VariantsGraph | None:
    """ Возвращает граф для варианта ответа """
    return VariantsGraph.objects.filter(variant_id=variant_id).first()

def update_variants_graph(variant_graph: VariantsGraph, variants_graph_data: dict) -> Variant:
    """ Обновление данных варианта по его идентификатору """
    for attr, value in variants_graph_data.items():
        setattr(variant_graph, attr, value)
    variant_graph.save()
    
    return variant_graph
