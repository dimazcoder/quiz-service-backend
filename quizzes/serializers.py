from datetime import datetime

import pytz
from attempts.serializers import AttemptSerializer
from attempts.services import get_attempt_for_quizz_and_attempter
from django.conf import settings
from questions.services import check_questions_existence_for_quizz
from rest_framework import serializers
from results.services import (check_results_existence_for_quizz,
                              check_results_without_graph_for_quizz)
from variants.services import check_variants_without_graph_for_quizz

from .models import (QUIZZ_STATUS_ACTIVE, QUIZZ_STATUS_NEW,
                     QUIZZ_TIME_TYPE_QUESTION, QUIZZ_TIME_TYPE_QUIZZ,
                     QUIZZ_TYPE_QUEST, Quizz, QuizzComplexity)


class QuizzSerializer(serializers.ModelSerializer):
    created_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    modified_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    active_attempt = serializers.SerializerMethodField('get_active_attempt')
    # active_attempt = QuizzActiveAttemptSerializer(many=True, queryset=Variant.objects.all())

    def get_active_attempt(self, quizz):
        """ Получает активную попытку для текущего участника, если она есть """
        request = self.context.get('request')
        if request and hasattr(request, 'attempter'):
            attempter = request.attempter
            attempt = get_attempt_for_quizz_and_attempter(quizz_id=quizz.id, attempter_id=attempter.id)
            return AttemptSerializer(instance=attempt, context=self.context).data if attempt else None

    def validate(self, attrs):
        quizz = getattr(self, 'instance', None)
    
        validation_errors = {}
        if 'time_type' in attrs and attrs['time_type'] in [QUIZZ_TIME_TYPE_QUESTION, QUIZZ_TIME_TYPE_QUIZZ]:
            passing_time = 0
            if 'passing_time' in attrs:
                passing_time = attrs['passing_time']
            elif quizz:
                passing_time = quizz.passing_time

            if passing_time <= 0:
                validation_errors['passing_time'] = 'Чтобы установить ограничение по времени нужно указать кол-во минут.'

        status = QUIZZ_STATUS_NEW
        if 'status' in attrs:
            status = attrs['status']
        elif quizz:
            status = quizz.status


        if quizz:
            auto_activation_at = attrs['auto_activation_at'] if 'auto_activation_at' in attrs else quizz.auto_activation_at
            is_auto_activation = attrs['is_auto_activation'] if 'is_auto_activation' in attrs else quizz.is_auto_activation
        else:
            is_auto_activation = False

        if is_auto_activation:
            tz = pytz.timezone(settings.TIME_ZONE)
            if auto_activation_at < datetime.now(tz):
                validation_errors['auto_activation_at'] = 'Дата автоматической активации не может быть раньше настоящего времени.'

        if status and status == QUIZZ_STATUS_ACTIVE:
            if quizz:
                questions_existence = check_questions_existence_for_quizz(quizz_id=quizz.id)

                if not questions_existence:
                    validation_errors['questions'] = 'В квизе нет вопросов.'

                results_existence = check_results_existence_for_quizz(quizz_id=quizz.id)

                if not results_existence:
                    validation_errors['results'] = 'В квизе нет результатов.'

                # Пробуем получить тип квиза из реквеста, либо берем текущий тип квиза
                quizz_type = attrs['quizz_type'] if hasattr(attrs, 'quizz_type') else quizz.quizz_type
                # quizz_type = quizz['quizz_type'] if 'quizz_type' in attrs else quizz.quizz_type

                if quizz_type == QUIZZ_TYPE_QUEST:
                    variants_without_graph = check_variants_without_graph_for_quizz(quizz_id=quizz.id)

                    if variants_without_graph:
                        validation_errors['variants'] = 'В квизе есть варианты ответа, для которых не задан граф.'

                    unused_results = check_results_without_graph_for_quizz(quizz_id=quizz.id)

                    if unused_results:
                        validation_errors['results'] = 'В квизе есть результаты, которые не привязаны ни к одному варианту ответа.'
            else:
                validation_errors['status'] = 'Чтобы установить статус "Активный" нужно создать вопросы, результаты и варианты ответов.'
                
        if validation_errors:
            raise serializers.ValidationError(validation_errors)

        return super().validate(attrs)

    class Meta:
        model = Quizz
        exclude = ('description',)

class QuizzComplexitySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizzComplexity
        fields = '__all__'
