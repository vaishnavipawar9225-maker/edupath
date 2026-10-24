import uuid
from django.db import models
from courses.models import Course
from accounts.models import User
from django.db import models
from accounts.models import User

class LiveClass(models.Model):                       # TABLE 18
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="live_classes")
    title = models.CharField(max_length=200)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    jitsi_room = models.CharField(max_length=100, unique=True, editable=False)
    recording_url = models.URLField(blank=True)

    class Meta:
        ordering = ["-scheduled_at"]

    def save(self, *args, **kwargs):
        if not self.jitsi_room:
            self.jitsi_room = f"edupath-{uuid.uuid4().hex[:10]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.title} - {self.title}"
    


class ParentMeeting(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("completed", "Completed"),
    ]
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meeting_requests")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher_meetings", limit_choices_to={"role": "teacher"})
    subject = models.CharField(max_length=100, help_text="e.g. Mathematics")
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parent.username} -> {self.teacher.username} on {self.date}"