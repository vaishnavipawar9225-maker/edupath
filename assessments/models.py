from django.db import models
from accounts.models import StudentProfile
from courses.models import Course, Chapter 

class Quiz(models.Model):                            # TABLE 11
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes")
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="quizzes", null=True, blank=True) 
    title = models.CharField(max_length=200)
    total_marks = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=15)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Question(models.Model):                        # TABLE 12
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text[:60]


class Choice(models.Model):                          # TABLE 13
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:50]


class QuizAttempt(models.Model):                     # TABLE 14
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def percentage(self):
        if not self.quiz.total_marks:
            return 0
        return round((self.score / self.quiz.total_marks) * 100, 2)


class StudentAnswer(models.Model):                   # TABLE 16
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True)
    is_correct = models.BooleanField(default=False)