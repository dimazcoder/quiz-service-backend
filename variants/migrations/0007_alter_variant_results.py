# Generated by Django 4.1.4 on 2023-01-30 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0003_alter_result_quizz'),
        ('variants', '0006_alter_variant_results'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variant',
            name='results',
            field=models.ManyToManyField(blank=True, related_name='variants', to='results.result', verbose_name='Результаты'),
        ),
    ]