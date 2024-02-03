from rest_framework import permissions


class IsQuestionOwnerOrReadOnly(permissions.BasePermission):
    """ Кастомный класс проверки прав, что текущий пользователь – создатель вопроса """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action in ['update', 'partial_update', 'destroy', 'create']:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action in ['update', 'partial_update', 'destroy']:
            return request.user.is_authenticated and obj.created_user and request.user == obj.created_user
        else:
            return False
