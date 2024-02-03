from django.conf import settings
from django.db import models


class Client(models.Model):
    """ Модель клиентов-держателей квизов (связка в квизах) """
    
    name = models.CharField('Имя клента-держателя', max_length=255)
    url = models.URLField('URL страницы авторизации', max_length=200)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    modified_at = models.DateTimeField('Дата редактирования', auto_now=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')


    class Meta:
        db_table = 'clients'
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f'Клиент "{self.name}"'
