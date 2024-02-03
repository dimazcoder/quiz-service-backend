import re

from quizzes.common_serializers import QuizzRelatedSerializer
from quizzes.models import QUIZZ_TYPE_SCORE, Quizz
from rest_framework import serializers

from .models import Result


class ResultSerializer(serializers.ModelSerializer):
    created_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    modified_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # quizz_id = serializers.PrimaryKeyRelatedField(source='quizz', queryset=Quizz.objects.all())
    quizz_id = QuizzRelatedSerializer(source='quizz', read_only=False, queryset=Quizz.objects.none())

    def validate(self, attrs):
        result = getattr(self, 'instance', None)

        if result:
            quizz = result.quizz
        else:
            quizz = attrs['quizz']

        validation_errors = {}

        if quizz.quizz_type == QUIZZ_TYPE_SCORE:
            try:
                scores_range = attrs['scores_range']

                if not re.match('^(\d+|0)-(\d+)$', scores_range):
                    validation_errors['scores_range'] = 'Некорректное значение диапазона баллов. Диапазон баллов должен быть в формате двух чисел разделенных дефисом.'
            except KeyError:
                if not result:
                    validation_errors['scores_range'] = 'Необходимо указать диапазон баллов для результата.'

        if validation_errors:
            raise serializers.ValidationError(validation_errors)

        return super().validate(attrs)

    def update(self, instance, validated_data):
        # Уберу квиз после валидации, чтобы нельзя было переносить результаты между квизами
        try:
            del validated_data['quizz']
        except KeyError:
            pass

        return super().update(instance, validated_data)

    class Meta:
        model = Result
        exclude = ('description', 'quizz',)
