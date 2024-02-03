from django.conf import settings
from django.db import models
from quizzes.models import Quizz


class Result(models.Model):
    """ Описание модели результатов для квизов """
    
    text = models.CharField('Результат', max_length=255)
    description = models.TextField('Очищенное описание', blank=True, editable=False) 
    description_original = models.TextField('Описание', blank=True)
    scores_range = models.CharField('Диапазон баллов (через дефис)', blank=True, max_length=20)
    quizz = models.ForeignKey(Quizz, on_delete=models.CASCADE, verbose_name='Квиз')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='results', verbose_name='Пользователь, создавший результат')
    modified_at = models.DateTimeField('Дата редактирования', auto_now=True)
    modified_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь, отредактировавший результат')
    
    class Meta:
        db_table = 'results'
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'

    def __str__(self):
        return f'Результат "{self.text}"'
