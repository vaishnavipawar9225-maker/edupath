from django.db import models
from accounts.models import User, StudentProfile
from courses.models import Course

class Attendance(models.Model):                      # TABLE 15
    STATUS = [("present", "Present"), ("absent", "Absent"), ("late", "Late")]
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS, default="present")
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    remark = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ("student", "course", "date")
        ordering = ["-date"]