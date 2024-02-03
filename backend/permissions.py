from quizzes.services import get_quizz_by_id
from rest_framework import permissions


class IsSuperuserOrReadOnly(permissions.BasePermission):
    """ Кастомный класс проверки прав, что текущий пользователь – суперпользователь """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated and request.user.is_superuser:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated and request.user.is_superuser:
            return True
        
        return False

class IsAuthenticatedOrOwnerOrReadOnly(permissions.BasePermission):
    """ 
    Кастомный класс проверки прав, что текущий пользователь – 
    аутентифицирован и является создателем объекта
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        if view.action == 'create':
            return request.user.is_authenticated
        elif view.action in ['update', 'partial_update', 'destroy']:
            return True

        return False
        
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action in ['update', 'partial_update', 'destroy']:
            return request.user.is_authenticated and request.user == obj.created_user
        
        return False

class IsAttempter(permissions.BasePermission):
    """ Проверка наличия attempter в request """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(request, 'attempter'):
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(request, 'attempter'):
            return True
        
        return False
