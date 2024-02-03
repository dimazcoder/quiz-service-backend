from rest_framework import permissions

from .services import get_attempt_by_id


class IsQuestionAttemptOwner(permissions.BasePermission):
    """ Проверка на то, что текущий участник является владельцем попытки привязанной к вопросу """
    def has_permission(self, request, view):

        if hasattr(request, 'attempter'):
            attempt_id = view.kwargs.get('attempt_id', None)
            if attempt_id:
                attempt = get_attempt_by_id(attempt_id=attempt_id)
                return attempt and attempt.attempter == request.attempter

        return False

    def has_object_permission(self, request, view, obj):
        """ Важно! Используется только во вьюсете работы с вопросами попытки и поэтому obj здесь это AttemptQuestion """
        if hasattr(request, 'attempter'):
            return obj.attempt.attempter == request.attempter

        return False

class IsAttemptOwner(permissions.BasePermission):
    """ 
    Проверка на то, что текущий участник является владельцем попытки.
    Пока только для retrieve т.к. общего списка попыток у нас нет. 
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(request, 'attempter'):
            return obj.attempter == request.attempter

        return False
