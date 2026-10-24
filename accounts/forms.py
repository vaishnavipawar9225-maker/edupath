
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, TeacherProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial="student"
    )
    phone = forms.CharField(max_length=15, required=False)
    grade = forms.ChoiceField(
        choices=[(str(i), f"Class {i}") for i in range(5, 11)],
        required=False,
        help_text="Only for students"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "role",
            "grade",
            "password1",
            "password2",
        ]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        grade = cleaned_data.get("grade")

        if role == "student" and not grade:
            self.add_error("grade", "Please select your class.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data.get("phone", "")
        user.role = self.cleaned_data["role"]
        
        if commit:
            user.save()
            # If they registered as a student, create StudentProfile
            if user.role == "student":
                grade = self.cleaned_data.get("grade") or 5
                StudentProfile.objects.create(user=user, grade=int(grade))
            
            # NEW: If they registered as a teacher, create TeacherProfile
            elif user.role == "teacher":
                TeacherProfile.objects.create(user=user)
                
        return user
