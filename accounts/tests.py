from django.test import TestCase
from .models import User, StudentProfile

class UserModelTest(TestCase):
    
    def test_create_student_user(self):
        """Test that a user can register as a student"""
        user = User.objects.create_user(username='teststudent', password='password123', role='student')
        self.assertEqual(user.role, 'student')
        self.assertTrue(user.check_password('password123'))
        
    def test_create_teacher_user(self):
        """Test that a user can register as a teacher"""
        user = User.objects.create_user(username='testteacher', password='password123', role='teacher')
        self.assertEqual(user.role, 'teacher')

    def test_student_profile_creation(self):
        """Test that a student profile correctly links to a User and saves the grade"""
        user = User.objects.create_user(username='student2', password='password123', role='student')
        profile = StudentProfile.objects.create(user=user, grade=9)
        
        self.assertEqual(profile.user.username, 'student2')
        self.assertEqual(profile.grade, 9)