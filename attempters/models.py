from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Attempter(models.Model):
    """Описание модели участников квизов"""

    email = models.EmailField("Электронный адрес", blank=True)
    phone_number = PhoneNumberField("Номер телефона", blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Пользователь",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    modified_at = models.DateTimeField("Дата редактирования", auto_now=True)

    class Meta:
        db_table = "attempters"
        verbose_name = "Участник"
        verbose_name_plural = "Участники"

    def __str__(self):
        return f"Участник {self.pk}"
