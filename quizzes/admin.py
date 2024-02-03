from django.contrib import admin

from .models import Quizz, QuizzComplexity


@admin.register(Quizz)
class QuizzAdmin(admin.ModelAdmin):
    list_display = ('title', 'alias', 'quizz_type', 'created_at',)
    readonly_fields = ('created_user', 'modified_user',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_user = request.user
        obj.modified_user = request.user
        super().save_model(request, obj, form, change)

@admin.register(QuizzComplexity)
class QuizzComplexityAdmin(admin.ModelAdmin):
    list_display = ('quizz_title', 'complexity', 'quantity', 'created_at',)

    def quizz_title(self, obj):
        return obj.quizz.title
