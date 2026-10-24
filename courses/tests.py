from django.test import TestCase
from accounts.models import User, StudentProfile
from .models import Subject, Course, Enrollment

class CourseModelTest(TestCase):

    def setUp(self):
        """Runs before every test to set up dummy data"""
        self.teacher = User.objects.create_user(username='verma', role='teacher')
        self.student_user = User.objects.create_user(username='riya', role='student')
        self.student = StudentProfile.objects.create(user=self.student_user, grade=10)
        
        self.subject = Subject.objects.create(name='Mathematics', grade=10)
        self.course = Course.objects.create(
            title='Algebra Mastery', 
            subject=self.subject, 
            teacher=self.teacher, 
            price=499
        )

    def test_course_creation(self):
        """Test if the course is created and the __str__ method works"""
        self.assertEqual(self.course.title, 'Algebra Mastery')
        self.assertEqual(str(self.course.subject), 'Mathematics (Class 10)')
        self.assertEqual(self.course.price, 499)

    def test_student_enrollment(self):
        """Test if a student can be enrolled in a course"""
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        
        self.assertEqual(enrollment.student.user.username, 'riya')
        self.assertEqual(self.course.enrollments.count(), 1)
        self.assertTrue(enrollment.is_active)