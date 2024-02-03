from django.contrib import admin

from .models import Variant, VariantsGraph


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('text', 'sort_order', 'question_text', 'created_at', 'modified_at')

    def question_text(self, obj):
        return f'Квиз "{obj.question.quizz.title}" вопрос "{obj.question.text}"'

@admin.register(VariantsGraph)
class VariantsGraphAdmin(admin.ModelAdmin):
    list_display = ('variant_text', 'next_question_text', 'result_text', 'created_at', 'modified_at')

    def variant_text(self, obj):
        return f'Квиз "{obj.variant.text}" вопрос "{obj.variant.question.text}"'
    
    def next_question_text(self, obj):
        return f'Квиз "{obj.next_question.quizz.title}" вопрос "{obj.next_question.text}"' if hasattr(obj, 'next_question') and obj.next_question is not None else ''

    def result_text(self, obj):
        return f'Результат "{obj.result.text}"' if hasattr(obj, 'result') and obj.result is not None else ''
