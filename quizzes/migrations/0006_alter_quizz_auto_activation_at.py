# Generated by Django 4.1.4 on 2023-04-04 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0005_quizz_is_auto_activation_alter_quizz_time_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizz',
            name='auto_activation_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата автоматической активации'),
        ),
    ]
