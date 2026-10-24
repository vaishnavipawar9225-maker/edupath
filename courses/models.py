from django.db import models
from accounts.models import User, StudentProfile

class Subject(models.Model):                         # TABLE 5
    name = models.CharField(max_length=100)
    grade = models.IntegerField()
    icon = models.CharField(max_length=50, default="bi-book")

    class Meta:
        unique_together = ("name", "grade")
        ordering = ["grade", "name"]

    def __str__(self):
        return f"{self.name} (Class {self.grade})"


class Course(models.Model):                          # TABLE 6
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="courses")
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 limit_choices_to={"role": "teacher"})
    thumbnail = models.ImageField(upload_to="courses/", blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_free = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Chapter(models.Model):                         # TABLE 7
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lecture(models.Model):                         # TABLE 8
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="lectures")
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True)
    pdf = models.FileField(upload_to="lectures/", blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]


class Enrollment(models.Model):                      # TABLE 9
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("student", "course")


class LectureProgress(models.Model):                 # TABLE 10
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    watched_seconds = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "lecture")