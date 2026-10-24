from django import forms
from liveclasses.models import ParentMeeting
from accounts.models import User

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