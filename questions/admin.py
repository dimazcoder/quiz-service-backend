from django.contrib import admin

from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'sort_order', 'quizz_title', 'is_start', 'created_at',)

    def quizz_title(self, obj):
        return obj.quizz.title
