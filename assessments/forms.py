from django import forms
from .models import Quiz
from courses.models import Course

class QuizCreateForm(forms.ModelForm):
    num_questions = forms.IntegerField(
        min_value=3, max_value=20, initial=5,
        help_text="How many questions to auto-generate (3–20)",
        widget=forms.NumberInput(attrs={"class": "form-input"}),
    )

    class Meta:
        model = Quiz
        fields = ["course", "title", "duration_minutes"]
        widgets = {
            "course": forms.Select(attrs={"class": "form-input"}),
            "title": forms.TextInput(attrs={"class": "form-input",
                                            "placeholder": "e.g. Algebra Quiz 2"}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-input"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # NEW LOGIC: Show ALL courses from Class 6 to 10
        self.fields["course"].queryset = Course.objects.filter(
            subject__grade__gte=6, 
            subject__grade__lte=10
        ).order_by('subject__grade', 'title')
        
        # Add a nice label for the dropdown
        self.fields["course"].label_from_instance = lambda obj: f"Class {obj.subject.grade} - {obj.subject.name}: {obj.title}"