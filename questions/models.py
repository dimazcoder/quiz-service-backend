from django.conf import settings
from django.db import models
from quizzes.models import Quizz

QUESSTION_GUESS_TYPE_ANY = 0
QUESSTION_GUESS_TYPE_ALL = 1

class Question(models.Model):
    """ Описание модели вопросов для квиза """

    QUESSTION_GUESS_TYPES = [
        (QUESSTION_GUESS_TYPE_ANY, 'Любой правильный ответ'),
        (QUESSTION_GUESS_TYPE_ALL, 'Все правильные ответы'),
    ]

    QUESTION_COMPLEXITIES = [
        (0, "0"),
        (1, "1"),
        (2, "2"),
        (3, "3"),
    ]

    text = models.CharField('Текст вопроса', max_length=1100)
    guess_type = models.SmallIntegerField('Нужно угадать', choices=QUESSTION_GUESS_TYPES, default=QUESSTION_GUESS_TYPE_ANY)
    correct_text = models.CharField('Текст правильного ответа', max_length=2200, blank=True)
    incorrect_text = models.CharField('Текст неправильного ответа', max_length=2200, blank=True)
    partially_correct_text = models.CharField('Текст частично правильного ответа', max_length=2200, blank=True)
    sort_order = models.PositiveIntegerField('Порядковый номер вопроса', blank=True, default=0)
    complexity = models.PositiveIntegerField('Сложность вопроса', choices=QUESTION_COMPLEXITIES, blank=True, default=1)
    is_start = models.BooleanField('Стартовый вопрос квиза', blank=True, default=False)
    quizz = models.ForeignKey(Quizz, on_delete=models.CASCADE, related_name='questions', verbose_name='Квиз')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='questions', verbose_name='Пользователь, создавший вопрос')
    modified_at = models.DateTimeField('Дата редактирования', auto_now=True)
    modified_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь, отредактировавший вопрос')

    def save(self, *args, **kwargs):
        # Если сохраняется вопрос с нулевым порядковым номером,
        # то ставим ему 1 если он первый для этого квиза,
        # либо устанавлием ему sort_order = кол-ву вопросов
        #
        if self.sort_order == 0:
            try:
                questions_count = Question.objects.filter(quizz_id=self.quizz_id).count()
                self.sort_order = questions_count if self.pk else questions_count + 1
            except Question.DoesNotExist:
                self.sort_order = 1

        # Стартовый вопрос может быть только один
        #
        if self.is_start:
            Question.objects.filter(quizz_id=self.quizz_id).update(is_start=False)

        super().save(*args, **kwargs)

    @property
    def count_variants_with_result(self) -> int:
        return self.variants.exclude(results__isnull=True).count()

    @property
    def count_variants_with_score(self) -> int:
        return self.variants.filter(complexity__gt=0).count()


    class Meta:
        db_table = 'questions'
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['sort_order']

    def __str__(self):
        return f'Вопрос "{self.text}" из теста "{self.quizz.title}"'
