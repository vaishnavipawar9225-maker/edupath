from django.contrib import admin
from .models import Subject, Course, Chapter, Lecture, Enrollment, LectureProgress

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "grade")
    list_filter = ("grade",)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "teacher", "price", "is_free")
    list_filter = ("subject__grade", "is_free")

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ("title", "chapter", "duration_minutes")

admin.site.register(Enrollment)
admin.site.register(LectureProgress)