from django.contrib import admin

from .models import Attempter


@admin.register(Attempter)
class AttempterAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone_number', 'created_at',)
