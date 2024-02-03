from django.db.models import Q, QuerySet

from .models import Result


def check_results_existence_for_quizz(quizz_id: int) -> bool:
    """ Проверяет наличие результатов для квиза """
    return Result.objects.filter(quizz_id=quizz_id).exists()

def check_results_without_graph_for_quizz(quizz_id: int) -> bool:
    """ Проверяет наличие результатов квиза к которым не привязан вариант ответа """
    return Result.objects.filter(quizz_id=quizz_id).filter(Q(graph__isnull=True)).exists()

def get_results_without_graph_for_quizz(quizz_id: int) -> QuerySet[Result]:
    """ Получение списка результатов, к которым не ведет ни один вариант ответа (граф) """
    try:
        return Result.objects.filter(quizz_id=quizz_id).filter(Q(graph__isnull=True))
    except Result.DoesNotExist:
        return None