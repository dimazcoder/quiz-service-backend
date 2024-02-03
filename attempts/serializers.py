from datetime import datetime, timedelta

import pytz
from attempters.serializers import AttempterSafeSerializer, AttempterSerializer
from django.conf import settings
from questions.models import QUESSTION_GUESS_TYPE_ALL
from questions.serializers import QuestionAttemptSerializer, QuestionSerializer
from questions.services import (get_start_question_for_quizz,
                                prepare_questions_for_quizz,
                                save_attempt_questions)
from quizzes.models import (QUIZZ_STATUS_ACTIVE, QUIZZ_TIME_TYPE_QUESTION,
                            QUIZZ_TIME_TYPE_QUIZZ, QUIZZ_TYPE_QUEST,
                            QUIZZ_TYPE_RESULT, QUIZZ_TYPE_SCORE, Quizz)
from rest_framework import serializers, status
from results.serializers import ResultSerializer
from variants.models import Variant
from variants.serializers import VariantWithoutQuestionSerializer

from backend.exceptions import CustomAPIException

from .models import Attempt, AttemptQuestion, AttemptResult
from .services import (check_attempt, get_active_attempt_question_for_attempt,
                       get_attempt_by_id,
                       get_attempt_question_by_attempt_and_sort_order,
                       get_attempts_for_quizz_and_attempter, update_attempt)


class AttemptQuizzSerializer(serializers.ModelSerializer):
    created_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    modified_user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Quizz
        exclude = ('description',)

class AttemptResultSerializer(serializers.ModelSerializer):
    result = ResultSerializer(read_only=True)
    class Meta:
        model = AttemptResult
        fields = '__all__'

class AttemptSerializer(serializers.ModelSerializer):
    attempter_id = serializers.PrimaryKeyRelatedField(source='attempter', read_only=True)
    attempter = AttempterSerializer(read_only=True)
    quizz_id = serializers.PrimaryKeyRelatedField(source='quizz', read_only=False, queryset=Quizz.objects.filter(status=QUIZZ_STATUS_ACTIVE))
    quizz = AttemptQuizzSerializer(read_only=True)
    attempt_question_no = serializers.SerializerMethodField('get_attempt_question_no')
    count_attempt_questions = serializers.SerializerMethodField('get_count_attempt_questions')
    results = serializers.SerializerMethodField('get_results')

    def get_results(self, instance):
        attempt_results = AttemptResult.objects.filter(attempt=instance)
        return [AttemptResultSerializer(attempt_result).data for attempt_result in attempt_results]

    def get_count_attempt_questions(self, instance):
        return instance.count_attempt_questions

    def get_attempt_question_no(self, attempt):
        active_attempt_question = get_active_attempt_question_for_attempt(attempt_id=attempt.id)
        return active_attempt_question.sort_order if active_attempt_question else 1

    def validate(self, attrs):
        request = self.context.get('request')
        if request and hasattr(request, 'attempter'):
            attempter = request.attempter
            attrs['attempter_id'] = attempter.id

        quizz = attrs['quizz']

        validation_errors = {}
        if quizz.count_attempts > 0:
            attempter_attempts = get_attempts_for_quizz_and_attempter(attempter_id=attrs['attempter_id'], quizz_id=quizz.id)
            if attempter_attempts and attempter_attempts.count() >= quizz.count_attempts:
                validation_errors['quizz'] = 'Вы использовали все доступные попытки на прохождение квиза.'

        if validation_errors:
            raise serializers.ValidationError(validation_errors)

        return super().validate(attrs)

    def create(self, validated_data):
        attempt = Attempt.objects.create(**validated_data)
        quizz = validated_data['quizz']
        attempter_id = validated_data['attempter_id']

        # Для квеста сохраняется только первый вопрос
        if quizz.quizz_type == QUIZZ_TYPE_QUEST:
            start_attempt_question = get_start_question_for_quizz(quizz_id=quizz.id)
            prepared_attempt_questions = [start_attempt_question]
        else:
            prepared_attempt_questions = prepare_questions_for_quizz(quizz=quizz, attempter_id=attempter_id)

        save_attempt_questions(attempt=attempt, questions=prepared_attempt_questions)
        return attempt

    # По идее, нам вообще не нужно обновлять попытку с фронта
    # Всё, что нужно – это ее создание и получение по идентификатору
    def update(self, instance, validated_data):
        # Уберу квиз после валидации, чтобы нельзя было переносить попытки между квизами
        try:
            del validated_data['quizz']
        except KeyError:
            pass

        instance = super().update(instance, validated_data)

        return instance

    class Meta:
        model = Attempt
        read_only_fields = ('guid', 'attempter', 'expired_at', 'results',)
        fields = '__all__'

class AttemptSafeSerializer(serializers.ModelSerializer):
    attempter_id = serializers.PrimaryKeyRelatedField(source='attempter', read_only=True)
    attempter = AttempterSafeSerializer(read_only=True)
    quizz_id = serializers.PrimaryKeyRelatedField(source='quizz', read_only=False, queryset=Quizz.objects.filter(status=QUIZZ_STATUS_ACTIVE))
    quizz = AttemptQuizzSerializer(read_only=True)
    attempt_question_no = serializers.SerializerMethodField('get_attempt_question_no')
    count_attempt_questions = serializers.SerializerMethodField('get_count_attempt_questions')
    results = serializers.SerializerMethodField('get_results')

    def get_results(self, instance):
        attempt_results = AttemptResult.objects.filter(attempt=instance)
        return [AttemptResultSerializer(attempt_result).data for attempt_result in attempt_results]

    def get_count_attempt_questions(self, instance):
        return instance.count_attempt_questions

    def get_attempt_question_no(self, attempt):
        active_attempt_question = get_active_attempt_question_for_attempt(attempt_id=attempt.id)
        return active_attempt_question.sort_order if active_attempt_question else 1

    class Meta:
        model = Attempt
        read_only_fields = ('guid', 'attempter', 'expired_at', 'results',)
        fields = '__all__'

class AttemptQuestionSerializer(serializers.ModelSerializer):
    # question = QuestionAttemptSerializer(read_only=True)
    question = serializers.SerializerMethodField('get_question')
    is_answered = serializers.SerializerMethodField('get_is_answered')
    variants = VariantWithoutQuestionSerializer(read_only=True, many=True)

    def get_is_answered(self, instance):
        return instance.is_answered


    def get_question(self, instance):
        if instance.is_answered:
            return QuestionSerializer(instance.question, read_only=True).data
        else:
            return QuestionAttemptSerializer(instance.question, read_only=True).data

    class Meta:
        model = AttemptQuestion
        fields = '__all__'

class AttemptQuestionVariantSerializer(serializers.PrimaryKeyRelatedField):
    """ Сериализатор для вариантов ответа, которые привязаны к вопросу, который передан в контексте """
    def get_queryset(self):
        attempt_id = self.context.get('attempt_id', None)
        attempt_question_sort_order = self.context.get('attempt_question_sort_order', None)
        attempt_question = get_attempt_question_by_attempt_and_sort_order(attempt_id=attempt_id, attempt_question_sort_order=attempt_question_sort_order)

        if attempt_question:
            return attempt_question.question.variants
        return super(AttemptQuestionVariantSerializer, self).get_queryset()

class AttemptQuestionUpdateSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    variants = AttemptQuestionVariantSerializer(many=True, queryset=Variant.objects.all())

    class Meta:
        model = AttemptQuestion
        fields = '__all__'

    def to_representation(self, instance):
        serializer = AttemptQuestionSerializer(instance)
        return serializer.data

    def validate(self, attrs):
        attempt_question = getattr(self, 'instance', None)
        attempt_id = self.context.get('attempt_id', None)
        attempt = get_attempt_by_id(attempt_id)

        try:
            variants = attrs['variants']
        except KeyError:
            variants = []

        validation_errors = {}

        if attempt_question and attempt_id and attempt_question.attempt.id != attempt_id:
            validation_errors['attempt_question_id'] = 'Некорректный attempt_question_id или attempt_id в URL эндпоинта. Вопрос с таким идентификатором не найден в рамках указанной попытки.'

        if attempt_question.is_answered and not attempt.quizz.is_free_navigation:
            validation_errors['variants'] = 'Нельзя исправлять ответы.'

        if len(variants) <= 0:
            validation_errors['variants'] = 'Нужно выбрать варинт ответа.'
        elif attempt.quizz.quizz_type in [QUIZZ_TYPE_QUEST, QUIZZ_TYPE_RESULT] and len(variants) > 1:
            validation_errors['variants'] = 'В данном типе квиза можно выбрать только один вариант ответа.'
        elif attempt.quizz.quizz_type == QUIZZ_TYPE_SCORE and attempt_question.question.guess_type == QUESSTION_GUESS_TYPE_ALL and len(variants) != attempt_question.question.count_variants_with_score:
            validation_errors['variants'] = 'Нужно выбрать вариантов ответа: ' + str(attempt_question.question.count_variants_with_score) + '.'

        if validation_errors:
            raise serializers.ValidationError(validation_errors)

        return super().validate(attrs)

    def update(self, instance, validated_data):
        attempt = instance.attempt

        tz = pytz.timezone(settings.TIME_ZONE)
        if attempt.quizz.time_type in [QUIZZ_TIME_TYPE_QUIZZ, QUIZZ_TIME_TYPE_QUESTION] and attempt.expired_at < datetime.now(tz):
            check_attempt(attempt_id=attempt.id)

            raise CustomAPIException(detail='Время на прохождение квиза истекло.', status_code=status.HTTP_400_BAD_REQUEST)
        else:
            instance = super().update(instance, validated_data)

            if attempt.quizz.quizz_type == QUIZZ_TYPE_QUEST:
                # Т.к. в квестах всегда один вариант ответа, то берем первый сохраненный и проверяем куда он "ведет"
                # Если к следующему вопросу, то сохраним его в пул вопросов попытки
                checked_attempt_question_variant = validated_data['variants'][0]

                if checked_attempt_question_variant.graph.next_question_id:
                    next_attempt_question = AttemptQuestion(attempt_id=attempt.id, question_id=checked_attempt_question_variant.graph.next_question_id)
                    next_attempt_question.save()

            if attempt.quizz.time_type in [QUIZZ_TIME_TYPE_QUESTION]:
                tz = pytz.timezone(settings.TIME_ZONE)
                update_attempt(attempt=attempt, attempt_data={
                    'expired_at': datetime.now(tz) + timedelta(minutes=attempt.quizz.passing_time)
                })

            check_attempt(attempt_id=attempt.id)

        return instance
