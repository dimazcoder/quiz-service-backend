from django.db.models import QuerySet

from .models import Quizz, QuizzComplexity


def get_quizz_by_id(quizz_id: int) -> Quizz | None:
    """ Получение квиза по его идентификатору """
    try:
        return Quizz.objects.get(pk=quizz_id)
    except Quizz.DoesNotExist:
        return None

def get_complexities_for_quizz(quizz_id: int) -> QuerySet[QuizzComplexity] | None:
    """ Получение сложностей для квиза """
    try:
        return QuizzComplexity.objects.filter(quizz_id=quizz_id)
    except QuizzComplexity.DoesNotExist:
        return None

def get_quizzes_for_user(user_id: int) -> QuerySet[Quizz] | None:
    """ Получение квизов для пользователя """
    try:
        return Quizz.objects.filter(created_user_id=user_id)
    except Quizz.DoesNotExist:
        return None
