from clients.models import Client
from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

QUIZZ_STATUS_NEW = 0
QUIZZ_STATUS_ACTIVE = 1

QUIZZ_TYPE_SCORE = 0
QUIZZ_TYPE_RESULT = 1
QUIZZ_TYPE_QUEST = 2

QUIZZ_TIME_TYPE_NONE = 0
QUIZZ_TIME_TYPE_QUESTION = 1
QUIZZ_TIME_TYPE_QUIZZ = 2

class Quizz(models.Model):
    """ Описание модели квизов """
    
    QUIZZ_STATUSES = [
        (QUIZZ_STATUS_NEW, 'Новый'),
        (QUIZZ_STATUS_ACTIVE, 'Активный'),
    ]

    QUIZZ_TYPES = [
        (QUIZZ_TYPE_SCORE, 'Баллы'),
        (QUIZZ_TYPE_RESULT, 'Соответствие результату'),
        (QUIZZ_TYPE_QUEST, 'Квест'),
    ]

    QUIZZ_TIME_TYPES = [
        (QUIZZ_TIME_TYPE_NONE, 'Без учета времени'),
        (QUIZZ_TIME_TYPE_QUESTION, 'Время на вопрос'),
        (QUIZZ_TIME_TYPE_QUIZZ, 'Время на квиз'),
    ]

    title = models.CharField('Название квиза', max_length=255)
    alias = models.CharField('Элиас квиза', max_length=50, unique=True, validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9\-\_]*?$',
                message='Алиас должен состоять из букв латинского алфавита, цифр, дефиса, подчеркивания.',
            ),
        ])
    description = models.TextField('Очищенное описание', blank=True, editable=False) 
    description_original = models.TextField('Описание', blank=True)
    quizz_type = models.SmallIntegerField('Тип квиза', choices=QUIZZ_TYPES, default=QUIZZ_TYPE_RESULT)
    time_type = models.SmallIntegerField('Ограничениe по времени', choices=QUIZZ_TIME_TYPES, default=QUIZZ_TIME_TYPE_NONE)
    count_results = models.PositiveIntegerField('Количество результатов в квизе', blank=True, default=1, validators = [
        MinValueValidator(
            limit_value=1, 
            message='Количество результатов не может быть меньше или равно нулю.',
        ),
    ])
    status = models.SmallIntegerField('Статус квиза', choices=QUIZZ_STATUSES, default=QUIZZ_STATUS_NEW)
    passing_time = models.PositiveIntegerField('Ограничение на прохождение (в минутах)', blank=True, default=0)
    count_attempts = models.PositiveIntegerField('Количество попыток', blank=True, default=0)
    is_random_questions = models.BooleanField('Вопросы в случайном порядке', default=False)
    count_questions = models.PositiveIntegerField('Количество вопросов', blank=True, default=0)
    is_submit_answer = models.BooleanField('Подтверждение ответа на вопрос по кнопке', default=False)
    is_free_navigation = models.BooleanField('Возможность перехода между вопросами', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quizzes', verbose_name='Пользователь, создавший квиз')
    modified_at = models.DateTimeField('Дата редактирования', auto_now=True)
    modified_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь, отредактировавший квиз')
    is_auto_activation = models.BooleanField('Автоматическая активация', default=False)
    auto_activation_at = models.DateTimeField('Дата автоматической активации', blank=True, null=True)
    clients = models.ManyToManyField(Client, related_name='clients', verbose_name='Клиенты')

    class Meta:
        db_table = 'quizzes'
        verbose_name = 'Квиз'
        verbose_name_plural = 'Квизы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Квиз "{self.title}"'

    def is_created_user(self, user: settings.AUTH_USER_MODEL) -> bool:
        return user == self.created_user

class QuizzComplexity(models.Model):
    """ 
    Описание модели сложностей в рамках теста: 
    отвечает за кол-во вопросов каждой сложности, которые могут использоваться в теста 
    """

    quizz = models.ForeignKey(Quizz, on_delete=models.CASCADE, related_name='complexities', verbose_name='Квиз')
    complexity = models.PositiveSmallIntegerField('Сложность вопроса', validators = [MinValueValidator(1)])
    quantity = models.PositiveSmallIntegerField('Количество вопросов', validators = [MinValueValidator(1)])
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quizz_complexities', verbose_name='Пользователь, добавивший сложность')
    modified_at = models.DateTimeField('Дата редактирования', auto_now=True)
    modified_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь, отредактировавший сложность')
    
    class Meta:
        db_table = 'quizz_complexities'
        verbose_name = 'Сложность'
        verbose_name_plural = 'Сложности'

    def __str__(self):
        return f'Квиз {self.quizz.title}, вопросов {self.quantity} со сложностью {self.complexity}'
