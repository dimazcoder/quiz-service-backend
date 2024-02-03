from django.conf import settings
from django.db import models
from questions.models import Question
from results.models import Result


class Variant(models.Model):
    """ Описание модели вариантов ответа на вопрос """

    text = models.CharField('Текст варианта ответа', max_length=1100)
    sort_order = models.PositiveIntegerField('Порядковый номер варианта ответа', blank=True, default=0)
    text_selected = models.TextField('Текст после выбора варианта', blank=True)
    complexity = models.IntegerField('Сложность (кол-во баллов выборе)', default=0)
    question = models.ForeignKey(Question, related_name='variants', on_delete=models.CASCADE, verbose_name='Вопрос')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='variants', verbose_name='Пользователь, создавший вариант ответа')
    modified_at = models.DateTimeField('Дата редактирования', auto_now=True)
    modified_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь, отредактировавший вариант ответа')
    results = models.ManyToManyField(Result, related_name='variants', blank=True, verbose_name='Результаты')

    def save(self, *args, **kwargs):
        # Если сохраняется вариант ответа с нулевым порядковым номером,
        # то ставим ему 1 если он первый для этого вопроса,
        # либо устанавлием ему sort_order = кол-ву вариантов ответа
        if self.sort_order == 0:
            try:
                variants_count = Variant.objects.filter(question_id=self.question_id).count()
                self.sort_order = variants_count if self.pk else variants_count + 1
            except Variant.DoesNotExist:
                self.sort_order = 1

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'variants'
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответа'
        ordering = ['sort_order']

    def __str__(self):
        return f'Вариант ответа: "{self.sort_order}. {self.text}"'

class VariantsGraph(models.Model):
    """ Описание модели графа вариантов ответа для типа теста "Квест" """

    variant = models.OneToOneField(Variant, on_delete=models.CASCADE, related_name='graph', verbose_name='Вариант ответа')
    next_question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Следующий вопрос')
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='graph', blank=True, null=True, verbose_name='Результат')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='graphs', verbose_name='Пользователь, создавший граф варианта ответа')
    modified_at = models.DateTimeField('Дата редактирования', auto_now=True)
    modified_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь, отредактировавший граф варианта ответа')

    class Meta:
        db_table = 'variants_graphs'
        verbose_name = 'Граф вариантов ответа'
        verbose_name_plural = 'Графы вариантов ответа'

    def __str__(self):
        return f'Граф варианта {self.variant.text}'
