# Generated by Django 4.1.4 on 2022-12-19 16:03

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Quizz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название квиза')),
                ('alias', models.CharField(max_length=50, unique=True, verbose_name='Элиас квиза')),
                ('description', models.TextField(blank=True, editable=False, verbose_name='Очищенное описание')),
                ('description_original', models.TextField(blank=True, verbose_name='Описание')),
                ('quizz_type', models.SmallIntegerField(choices=[(0, 'Баллы'), (1, 'Соответствие результату'), (2, 'Квест')], default=0, verbose_name='Тип квиза')),
                ('time_type', models.SmallIntegerField(choices=[(0, 'Без учета времени'), (1, 'Время на вопрос'), (2, 'Время на тест')], default=0, verbose_name='Ограничени по времени')),
                ('count_results', models.PositiveIntegerField(default=1, verbose_name='Количество результатов в квизе')),
                ('status', models.SmallIntegerField(choices=[(0, 'Новый'), (1, 'Активный')], default=0, verbose_name='Статус квиза')),
                ('passing_time', models.PositiveIntegerField(blank=True, default=0, verbose_name='Ограничение на прохождение (в минутах)')),
                ('count_attempts', models.PositiveIntegerField(blank=True, default=0, verbose_name='Количество попыток')),
                ('is_random_questions', models.BooleanField(default=False, verbose_name='Вопросы в случайном порядке')),
                ('count_questions', models.PositiveIntegerField(blank=True, default=0, verbose_name='Количество вопросов')),
                ('is_submit_answer', models.BooleanField(default=False, verbose_name='Подтверждение ответа на вопрос по кнопке')),
                ('is_free_navigation', models.BooleanField(default=False, verbose_name='Возможность перехода между вопросами')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Дата редактирования')),
                ('auto_activation_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата автоматической активации')),
                ('clients', models.ManyToManyField(related_name='clients', to='clients.client', verbose_name='Клиенты')),
                ('created_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, создавший квиз')),
                ('modified_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, отредактировавший квиз')),
            ],
            options={
                'verbose_name': 'Квиз',
                'verbose_name_plural': 'Квизы',
                'db_table': 'quizzes',
            },
        ),
        migrations.CreateModel(
            name='QuizzComplexity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('complexity', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Сложность вопроса')),
                ('quantity', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество вопросов')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Дата редактирования')),
                ('created_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizz_complexities', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, добавивший сложность')),
                ('modified_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, отредактировавший сложность')),
                ('quizz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complexities', to='quizzes.quizz', verbose_name='Квиз')),
            ],
            options={
                'verbose_name': 'Сложность',
                'verbose_name_plural': 'Сложности',
                'db_table': 'quizz_complexities',
            },
        ),
    ]
