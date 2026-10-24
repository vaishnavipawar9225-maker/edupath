from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Enrollment
from .models import LiveClass

@login_required
def live_list(request):
    classes = LiveClass.objects.select_related("course").all()
    if request.user.role == "student":
        enrolled_ids = Enrollment.objects.filter(
            student=request.user.student_profile
        ).values_list("course_id", flat=True)
        classes = classes.filter(course_id__in=enrolled_ids)
    return render(request, "liveclasses/list.html", {"classes": classes})

@login_required
def join_class(request, pk):
    live = get_object_or_404(LiveClass, pk=pk)
    error = None
    if request.user.role == "student":
        if not Enrollment.objects.filter(student=request.user.student_profile, course=live.course).exists():
            error = "You must be enrolled in this course to join."
    return render(request, "liveclasses/join.html", {"live_class": live, "error": error})