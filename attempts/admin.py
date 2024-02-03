from django.contrib import admin

from .models import Attempt, AttemptQuestion


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('guid', 'quizz_title', 'attempter_email', 'result_text', 'created_at',)
    readonly_fields = ('guid', 'created_at', 'modified_at',)

    def quizz_title(self, obj):
        return obj.quizz.title

    def attempter_email(self, obj):
        return obj.attempter.email

    def result_text(self, obj):
        return obj.result.text if hasattr(obj, 'result') and obj.result is not None else ''

@admin.register(AttemptQuestion)
class AttemptQuestionAdmin(admin.ModelAdmin):
    list_display = ('attempt_guid', 'question_text', 'created_at',)

    def attempt_guid(self, obj):
        return obj.attempt.guid

    def question_text(self, obj):
        return obj.question.text
