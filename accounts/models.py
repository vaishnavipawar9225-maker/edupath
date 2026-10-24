from django.db import models
from django.contrib.auth.models import AbstractUser

GRADE_CHOICES = [(i, f"Class {i}") for i in range(5, 11)]

class User(AbstractUser):                            # TABLE 1
    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("parent", "Parent"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class StudentProfile(models.Model):                  # TABLE 2
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    grade = models.IntegerField(choices=GRADE_CHOICES, default=5)
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="children", limit_choices_to={"role": "parent"})
    enrollment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Class {self.grade}"


class TeacherProfile(models.Model):                  # TABLE 3
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    subjects = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Teacher: {self.user.username}"


class ParentProfile(models.Model):                   # TABLE 4
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="parent_profile")
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Parent: {self.user.username}"