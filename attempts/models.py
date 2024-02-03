import hashlib
from datetime import datetime, timedelta

import pytz
from attempters.models import Attempter
from django.conf import settings
from django.db import models
from django.utils import timezone
from questions.models import Question
from quizzes.models import (QUIZZ_TIME_TYPE_QUESTION, QUIZZ_TIME_TYPE_QUIZZ,
                            Quizz)
from results.models import Result
from variants.models import Variant


class Attempt(models.Model):
    """ Описание модели попытки прохождения квиза """
    guid = models.CharField('Уникальный hash попытки', max_length=32, blank=True, null=True)
    quizz = models.ForeignKey(Quizz, on_delete=models.CASCADE, verbose_name='Квиз')
    attempter = models.ForeignKey(Attempter, on_delete=models.CASCADE, verbose_name='Участник')
    results = models.ManyToManyField(Result, through='AttemptResult', verbose_name='Результаты попытки')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    modified_at = models.DateTimeField('Дата редактирования', auto_now=True)
    expired_at = models.DateTimeField('Дата истечения', blank=True, null=True)

    def save(self, *args, **kwargs):
        # При создании попытки формируем уникальный GUID
        self.guid = self.guid if self.pk else hashlib.md5((str(self.quizz_id) + str(self.attempter.id) + str(timezone.now())).encode('utf-8')).hexdigest()

        if not self.pk and self.quizz.time_type in [QUIZZ_TIME_TYPE_QUIZZ, QUIZZ_TIME_TYPE_QUESTION]:
            tz = pytz.timezone(settings.TIME_ZONE)
            self.expired_at = datetime.now(tz) + timedelta(minutes=self.quizz.passing_time)

        super().save(*args, **kwargs)

    @property
    def count_attempt_questions(self) -> int:
        return self.attempt_questions.count()

    class Meta:
        db_table = 'attempts'
        verbose_name = 'Попытка'
        verbose_name_plural = 'Попытки'

    def __str__(self):
        return f'Попытка "{self.guid}"'

class AttemptResult(models.Model):
    """ Описание модели-связки для сохранения результатов по итогам попытки """
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, verbose_name='Попытка')
    result = models.ForeignKey(Result, on_delete=models.CASCADE, verbose_name='Результат попытки')
    correct_answers = models.PositiveIntegerField('Кол-во ответов для этого результата', blank=True, default=0)
    score = models.PositiveIntegerField('Кол-во баллов попытки', blank=True, default=0)
    percent = models.PositiveIntegerField('Процент ответов с этим результатов', blank=True, default=0)
    total_percent = models.PositiveIntegerField('Процент правильных ответов', blank=True, default=0)
    correct_answers_percent = models.PositiveIntegerField('Процент правильных ответов для этого результата', blank=True, default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    modified_at = models.DateTimeField('Дата редактирования', auto_now=True)

    class Meta:
        db_table = 'attempt_results'
        verbose_name = 'Результат попытки'
        verbose_name_plural = 'Результаты попыток'
        unique_together = ['attempt', 'result']

class AttemptQuestion(models.Model):
    """ Описание модели вопросов в рамках попытки """
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='attempt_questions', verbose_name='Попытка')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    sort_order = models.PositiveIntegerField('Порядковый номер вопроса', blank=True, default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    modified_at = models.DateTimeField('Дата редактирования', auto_now=True)
    variants = models.ManyToManyField(Variant, through='AttemptQuestionVariant', verbose_name='Варианты ответа', blank=True)

    def save(self, *args, **kwargs):
        # Если сохраняется вопрос с нулевым порядковым номером,
        # то ставим ему 1 если он первый для этого квиза,
        # либо устанавлием ему sort_order = кол-ву вопросов
        if self.sort_order == 0:
            try:
                questions_count = AttemptQuestion.objects.filter(attempt_id=self.attempt_id).count()
                self.sort_order = questions_count if self.pk else questions_count + 1
            except AttemptQuestion.DoesNotExist:
                self.sort_order = 1

        super().save(*args, **kwargs)

    @property
    def is_answered(self) -> bool:
        return self.variants.exists()

    class Meta:
        db_table = 'attempt_questions'
        verbose_name = 'Вопрос в рамках попытки'
        verbose_name_plural = 'Вопросы в рамках попытки'
        unique_together = ['attempt', 'sort_order']

    def __str__(self):
        return f'Попытка "{self.attempt.guid}", вопрос "{self.question.text}"'

class AttemptQuestionVariant(models.Model):
    """ Описание модели ответов на вопросы в рамках попытки """
    attempt_question = models.ForeignKey(AttemptQuestion, on_delete=models.CASCADE, verbose_name='Вопрос в рамках попытки')
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, verbose_name='Вариант ответа на вопрос в рамках попытки')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    modified_at = models.DateTimeField('Дата редактирования', auto_now=True)

    class Meta:
        db_table = 'attempt_question_variants'
        verbose_name = 'Вариант ответа в рамках попытки'
        verbose_name_plural = 'Варианты ответа в рамках попытки'
        unique_together = ['attempt_question', 'variant',]

    def __str__(self):
        return f'Вариант ответа "{self.variant.text}"'
