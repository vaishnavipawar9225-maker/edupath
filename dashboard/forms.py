from django import forms
from liveclasses.models import ParentMeeting
from accounts.models import User
from django import forms
from liveclasses.models import LiveClass
from courses.models import Course

class MeetingForm(forms.ModelForm):
    class Meta:
        model = LiveClass
        fields = ['course', 'title', 'scheduled_at', 'duration_minutes']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-input'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Doubt Clearing Session'}),
            'scheduled_at': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 60'}),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            # Only show courses that belong to this teacher
            self.fields['course'].queryset = Course.objects.filter(teacher=teacher)
            
            
class MeetingRequestForm(forms.ModelForm):
    class Meta:
        model = ParentMeeting
        fields = ["teacher", "subject", "date", "time"]
        widgets = {
            "teacher": forms.Select(attrs={"class": "form-input"}),
            "subject": forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. Mathematics"}),
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "time": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users who are teachers in the dropdown
        self.fields["teacher"].queryset = User.objects.filter(role="teacher")
        
class LinkChildForm(forms.Form):
    student_email = forms.EmailField(
        label="Student's Email Address",
        widget=forms.EmailInput(attrs={
            "class": "form-input", 
            "placeholder": "e.g., riya@edupath.in"
        })
    )