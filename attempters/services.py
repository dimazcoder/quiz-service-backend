from django.contrib.auth import get_user_model

from .models import Attempter


User = get_user_model()

def create_attempter(user: User = None, email: str = '', phone_number: str = '') -> Attempter:
    """ Создание участника квиза """
    attempter = Attempter.objects.create(user=user, email=email, phone_number=phone_number)
    return attempter

def get_attempter_for_user(user_id: int) -> Attempter | None:
    """ Получение записи участника по идентификатору пользователя """
    try:
        return Attempter.objects.get(user_id=user_id)
    except Attempter.DoesNotExist:
        return None

def get_attempter_by_id(attempter_id: int) -> Attempter | None:
    """ Получение участника по его идентификатору """
    try:
        return Attempter.objects.get(pk=attempter_id)
    except Attempter.DoesNotExist:
        return None
