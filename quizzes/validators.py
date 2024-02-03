from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_auto_activation_date(value):
    """ Валидация даты автоматической активации квиза """
    if value < timezone.now():
        raise ValidationError(message='Дата автоматической активации не может быть раньше настоящего времени.',
            params={'value': value})
