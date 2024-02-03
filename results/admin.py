from django.contrib import admin

from .models import Result


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('text', 'quizz_title', 'created_at',)

    def quizz_title(self, obj):
        return obj.quizz.title
