from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from courses.models import Course, Enrollment
from .models import Attendance

@login_required
def mark_attendance(request, course_id):
    if request.user.role not in ("teacher", "admin"):
        messages.error(request, "Only teachers can mark attendance.")
        return redirect("dashboard")
    course = get_object_or_404(Course, pk=course_id)
    students = Enrollment.objects.filter(course=course, is_active=True).select_related("student__user")
    today = timezone.now().date()

    if request.method == "POST":
        date_str = request.POST.get("date", str(today))
        for e in students:
            status = request.POST.get(f"status_{e.student.id}", "absent")
            Attendance.objects.update_or_create(
                student=e.student, course=course, date=date_str,
                defaults={"status": status, "marked_by": request.user}
            )
        messages.success(request, f"Attendance saved for {date_str}")
        return redirect("mark_attendance", course_id=course_id)

    existing = {a.student_id: a.status for a in Attendance.objects.filter(course=course, date=today)}
    return render(request, "attendance/mark.html", {
        "course": course, "students": students, "today": today, "existing": existing,
    })

@login_required
def my_attendance(request):
    if request.user.role != "student":
        return redirect("dashboard")
    records = Attendance.objects.filter(student=request.user.student_profile)
    total = records.count()
    present = records.filter(status="present").count()
    percent = round((present / total * 100) if total else 0, 1)
    return render(request, "attendance/list.html", {
        "records": records, "total": total, "present": present, "percent": percent,
    })