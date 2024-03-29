# Generated by Django 4.1.4 on 2022-12-19 16:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quizzes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255, verbose_name='Результат')),
                ('description', models.TextField(blank=True, editable=False, verbose_name='Очищенное описание')),
                ('description_original', models.TextField(blank=True, verbose_name='Описание')),
                ('scores_range', models.CharField(max_length=20, verbose_name='Диапазон баллов (через дефис)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Дата редактирования')),
                ('created_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, создавший результат')),
                ('modified_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, отредактировавший результат')),
                ('quizz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizzes.quizz', verbose_name='Квиз')),
            ],
            options={
                'verbose_name': 'Результат',
                'verbose_name_plural': 'Результаты',
                'db_table': 'results',
            },
        ),
    ]
