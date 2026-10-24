from django.test import TestCase
from accounts.models import User, StudentProfile
from courses.models import Subject, Course
from .models import Quiz, QuizAttempt

class QuizLogicTest(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher1', role='teacher')
        self.student_user = User.objects.create_user(username='student1', role='student')
        self.student = StudentProfile.objects.create(user=self.student_user, grade=10)
        
        self.subject = Subject.objects.create(name='Science', grade=10)
        self.course = Course.objects.create(title='Physics', subject=self.subject, teacher=self.teacher)
        
        # Create a quiz worth 10 marks
        self.quiz = Quiz.objects.create(course=self.course, title='Physics Quiz 1', total_marks=10)

    def test_percentage_calculation(self):
        """Test if the percentage is calculated correctly (8 out of 10 = 80%)"""
        attempt = QuizAttempt.objects.create(student=self.student, quiz=self.quiz, score=8)
        self.assertEqual(attempt.percentage(), 80.0)

    def test_percentage_zero_total_marks(self):
        """Test edge case: if total_marks is 0, it shouldn't crash (ZeroDivisionError)"""
        self.quiz.total_marks = 0
        self.quiz.save()
        
        attempt = QuizAttempt.objects.create(student=self.student, quiz=self.quiz, score=0)
        self.assertEqual(attempt.percentage(), 0)