from datetime import datetime

import pytz
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Count, QuerySet
from questions.models import Question
from quizzes.models import (QUIZZ_TIME_TYPE_QUESTION, QUIZZ_TIME_TYPE_QUIZZ,
                            QUIZZ_TYPE_QUEST, QUIZZ_TYPE_SCORE)
from rest_framework import status
from results.models import Result

from backend.exceptions import CustomAPIException

from .models import (Attempt, AttemptQuestion, AttemptQuestionVariant,
                     AttemptResult)


def get_asked_questions_for_attempter_in_quizz(attempter_id: int, quizz_id: int) -> QuerySet[Question] | None:
    """ Получение списка вопросов, на которые участник отвечал в рамках квиза """
    attempt_questions_for_attempter_and_quizz = AttemptQuestion.objects.values('question_id').filter(
        attempt_id__in=Attempt.objects.filter(attempter_id=attempter_id),
        attempt__quizz_id=quizz_id
    ).annotate(question_count=Count('question_id'))

    if not attempt_questions_for_attempter_and_quizz:
        return None

    asked_question_ids = attempt_questions_for_attempter_and_quizz.values_list('question_id', flat=True)

    try:
        return Question.objects.filter(id__in=asked_question_ids)
    except Question.DoesNotExist:
       return None

def get_attempt_by_id(attempt_id: int) -> Attempt | None:
    """ Получение попытки по идентификатору """
    try:
        return Attempt.objects.get(pk=attempt_id)
    except Attempt.DoesNotExist:
        return None

def get_attempt_questions(attempt_id:int) -> QuerySet[AttemptQuestion] | None:
    """ Получение списка вопросов по идентификатору попытки """
    try:
        return AttemptQuestion.objects.select_related('question').filter(attempt_id=attempt_id).prefetch_related('question__variants', 'question__variants__results').order_by('sort_order')
    except AttemptQuestion.DoesNotExist:
       return None

def get_attempt_question_by_id(attempt_question_id: int) -> AttemptQuestion | None:
    """ Получение вопроса по его идентификатору в рамках попытки """
    try:
        return AttemptQuestion.objects.get(pk=attempt_question_id)
    except AttemptQuestion.DoesNotExist:
        return None

def get_active_attempt_question_for_attempt(attempt_id: int) -> int:
    """ Получение текущего активного вопроса в рамках попытки """
    return AttemptQuestion.objects.filter(
            attempt_id=attempt_id,
        ).exclude(variants__isnull=False).order_by('sort_order').first()

def get_attempt_for_quizz_and_attempter(quizz_id: int, attempter_id: int) -> Attempt | None:
    """ Получение активной попытки для квиза и участника """
    return Attempt.objects.filter(
        quizz_id=quizz_id, attempter_id=attempter_id
    ).order_by('-pk').first()

def check_attempt(attempt_id: int) -> bool:
    """ Проверяет попытку и возвращает bool в зависимости от результата """
    attempt = Attempt.objects.select_related('quizz').get(pk=attempt_id)
    if not attempt:
        raise CustomAPIException('Попытка не найдена.', status_code=status.HTTP_404_NOT_FOUND)

    quizz = attempt.quizz

    attempt_finished = False
    
    if quizz.quizz_type == QUIZZ_TYPE_QUEST:
        checked_attempt_question_variant = AttemptQuestionVariant.objects.prefetch_related('variant').select_related('variant__graph').filter(attempt_question__attempt_id=attempt.id).order_by('-attempt_question_id').first()
        if not checked_attempt_question_variant:
            raise CustomAPIException('Не найден ответ на предыдущий вопрос.', status_code=status.HTTP_404_NOT_FOUND)

        if not checked_attempt_question_variant.variant.graph:
            raise CustomAPIException('Для выбранного варианта ответа не указан граф.', status_code=status.HTTP_404_NOT_FOUND)

        if checked_attempt_question_variant.variant.graph.result_id:
            attempt_result = AttemptResult(attempt_id=attempt.id, result_id=checked_attempt_question_variant.variant.graph.result_id)
            attempt_result.save()

            attempt_finished = True
    else:
        if quizz.time_type in [QUIZZ_TIME_TYPE_QUIZZ, QUIZZ_TIME_TYPE_QUESTION]:
            tz = pytz.timezone(settings.TIME_ZONE)
            if (attempt.expired_at and attempt.expired_at < datetime.now(tz)):
                attempt_finished = True

        if not attempt_finished:
            count_answered_questions = AttemptQuestion.objects.filter(attempt_id=attempt.id).exclude(variants__isnull=True).count()
            count_attempt_questions = AttemptQuestion.objects.filter(attempt_id=attempt.id).count()

            attempt_finished = count_answered_questions >= count_attempt_questions
        
        if attempt_finished:
            available_results = Result.objects.filter(quizz_id=quizz.id)
            attempt_tmp_results = {}
            attempt_results = []

            for result in available_results:
                attempt_tmp_results[result.id] = {
                    'result_id': result.id,
                    'scores_range': result.scores_range,
                    'percent': 0, 
                    'correct_answers': 0, 
                    'score': 0,
                    'total_percent': 0,
                    'correct_answers_percent': 0
                }

            if quizz.quizz_type == QUIZZ_TYPE_SCORE:
                attempt_variants = AttemptQuestionVariant.objects.filter(
                    attempt_question__attempt_id=attempt.id
                ).select_related('variant', 'attempt_question', 'attempt_question__question').prefetch_related('variant__results')
                
                total_score = 0

                for attempt_variant in attempt_variants:
                    total_score = total_score + attempt_variant.variant.complexity

                for _, attempt_tmp_result in attempt_tmp_results.items():
                    lower_value, upper_value = [int(n) for n in attempt_tmp_result['scores_range'].split('-')]
                    if total_score >= lower_value and total_score <= upper_value:
                        attempt_results.append({**attempt_tmp_result, 'score': total_score})
                        break
            else:
                attempt_variants = AttemptQuestionVariant.objects.filter(
                    attempt_question__attempt_id=attempt.id
                ).select_related('variant', 'attempt_question', 'attempt_question__question').prefetch_related('variant__results').exclude(variant__results__isnull=True)
                
                total_count_correct_answers = 0
                for attempt_variant in attempt_variants:
                    if attempt_variant.variant.results:
                        total_count_correct_answers = total_count_correct_answers + 1
                        for attempt_variant_result in attempt_variant.variant.results.all():
                            attempt_tmp_results[attempt_variant_result.id] = {
                                **attempt_tmp_results[attempt_variant_result.id], 
                                'correct_answers': attempt_tmp_results[attempt_variant_result.id]['correct_answers'] + 1,
                                'score': attempt_tmp_results[attempt_variant_result.id]['score'] + attempt_variant.attempt_question.question.complexity,
                                'percent': attempt_tmp_results[attempt_variant_result.id]['percent'] + (100 / attempt.count_attempt_questions)
                            }
                
                for attempt_tmp_result in attempt_tmp_results.values():
                    attempt_results.append({
                        **attempt_tmp_result, 
                        'total_percent': round(total_count_correct_answers * (100 / attempt.count_attempt_questions)) if total_count_correct_answers > 0 else 0,
                        'correct_answers_percent': round(attempt_tmp_result['correct_answers'] * (100 / total_count_correct_answers)) if total_count_correct_answers > 0 else 0
                    })

            attempt_results = sorted(attempt_results, key=lambda d: d['percent'], reverse=True)

            attempt_results_sliced = attempt_results[:quizz.count_results] if quizz.count_results > len(attempt_results) else attempt_results

            for attempt_result_sliced in attempt_results_sliced:
                try:
                    attempt_result = AttemptResult(
                        attempt_id=attempt.id, 
                        result_id=attempt_result_sliced['result_id'],
                        correct_answers=attempt_result_sliced['correct_answers'],
                        score=attempt_result_sliced['score'],
                        percent=attempt_result_sliced['percent'],
                        total_percent=attempt_result_sliced['total_percent'],
                        correct_answers_percent=attempt_result_sliced['correct_answers_percent'],
                    )
                    attempt_result.save()
                except IntegrityError as e:
                    attempt_result = AttemptResult.objects.filter(attempt_id=attempt.id, result_id=attempt_result_sliced['result_id']).first()
                    attempt_result.correct_answers = attempt_result_sliced['correct_answers']
                    attempt_result.score = attempt_result_sliced['score']
                    attempt_result.percent = attempt_result_sliced['percent']
                    attempt_result.total_percent = attempt_result_sliced['total_percent']
                    attempt_result.correct_answers_percent = attempt_result_sliced['correct_answers_percent']
                    
                    attempt_result.save()


    return attempt_finished

def get_attempt_question_by_attempt_and_sort_order(attempt_id: int, attempt_question_sort_order: int) -> AttemptQuestion | None:
    """ Получение вопроса по идентификатору поытки и порядковому номеру """
    try:
        return AttemptQuestion.objects.get(attempt_id=attempt_id, sort_order=attempt_question_sort_order)
    except AttemptQuestion.DoesNotExist:
        return None

def update_attempt(attempt: Attempt, attempt_data: dict) -> Attempt:
    """ Обновление данных попытки по её идентификатору """
    for attr, value in attempt_data.items():
        setattr(attempt, attr, value)
    attempt.save()
    
    return attempt

def get_attempts_for_quizz_and_attempter(quizz_id: int, attempter_id: int) -> QuerySet[Attempt] | None:
    """ Получение активной попытки для квиза и участника """
    try:
        return Attempt.objects.filter(
            quizz_id=quizz_id, attempter_id=attempter_id
        ).order_by('-pk')
    except Attempt.DoesNotExist:
        return None