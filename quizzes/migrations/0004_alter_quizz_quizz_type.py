# Generated by Django 4.1.4 on 2023-03-10 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0003_alter_quizz_alias_alter_quizz_auto_activation_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizz',
            name='quizz_type',
            field=models.SmallIntegerField(choices=[(0, 'Баллы'), (1, 'Соответствие результату'), (2, 'Квест')], default=1, verbose_name='Тип квиза'),
        ),
    ]
