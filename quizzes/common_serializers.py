from rest_framework import serializers

from .models import Quizz
from .services import get_quizzes_for_user


class QuizzRelatedSerializer(serializers.PrimaryKeyRelatedField):
    """ Сериализатор для квизов, которые доступны текущему юзеру """
    def get_queryset(self):
        user = self.context['request'].user
        if user.is_authenticated:
            if user.is_superuser:
                return Quizz.objects.all()
            elif user.is_authenticated:
                return get_quizzes_for_user(user_id=user.id)

        return super(QuizzRelatedSerializer, self).get_queryset()