# Generated by Django 4.1.4 on 2022-12-22 10:56

import django.core.validators
from django.db import migrations, models
import quizzes.validators


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0002_alter_quizz_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizz',
            name='alias',
            field=models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator(message='Алиас должен состоять из букв латинского алфавита, цифр, дефиса, подчеркивания.', regex='^[a-zA-Z0-9\\-\\_]*?$')], verbose_name='Элиас квиза'),
        ),
        migrations.AlterField(
            model_name='quizz',
            name='auto_activation_at',
            field=models.DateTimeField(blank=True, null=True, validators=[quizzes.validators.validate_auto_activation_date], verbose_name='Дата автоматической активации'),
        ),
        migrations.AlterField(
            model_name='quizz',
            name='count_results',
            field=models.PositiveIntegerField(blank=True, default=1, validators=[django.core.validators.MinValueValidator(limit_value=1, message='Количество результатов не может быть меньше или равно нулю.')], verbose_name='Количество результатов в квизе'),
        ),
        migrations.AlterField(
            model_name='quizz',
            name='time_type',
            field=models.SmallIntegerField(choices=[(0, 'Без учета времени'), (1, 'Время на вопрос'), (2, 'Время на квиз')], default=0, verbose_name='Ограничени по времени'),
        ),
    ]
