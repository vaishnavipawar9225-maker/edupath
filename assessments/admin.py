from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, StudentAnswer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "total_marks", "is_published")
    list_filter = ("is_published",)

admin.site.register(QuizAttempt)
admin.site.register(StudentAnswer)