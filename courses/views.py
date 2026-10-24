
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Course, Lecture, Enrollment, LectureProgress, Subject


def course_list(request):
    """Display all courses, optionally filtered by class/grade."""
    grade = request.GET.get("grade")

    courses = Course.objects.select_related(
        "subject", "teacher"
    ).prefetch_related("chapters")

    if grade:
        if grade in {"5", "6", "7", "8", "9", "10"}:
            courses = courses.filter(subject__grade=int(grade))
        else:
            messages.warning(request, "Please select a valid class.")

    return render(
        request,
        "courses/list.html",
        {"courses": courses, "selected_grade": grade},
    )


def course_detail(request, pk):
    """Show course information and enrollment status."""
    course = get_object_or_404(
        Course.objects.select_related("subject", "teacher").prefetch_related(
            "chapters__lectures"
        ),
        pk=pk,
    )

    enrolled = False

    if request.user.is_authenticated and request.user.role == "student":
        try:
            student = request.user.student_profile
            enrolled = Enrollment.objects.filter(
                student=student,
                course=course,
                is_active=True,
            ).exists()
        except AttributeError:
            enrolled = False

    return render(
        request,
        "courses/detail.html",
        {"course": course, "enrolled": enrolled},
    )


@login_required
def lecture_view(request, pk):
    """Allow enrolled students to access course lectures."""
    lecture = get_object_or_404(
        Lecture.objects.select_related(
            "chapter__course__subject"
        ),
        pk=pk,
    )

    course = lecture.chapter.course
    progress = None

    if request.user.role == "student":
        try:
            student = request.user.student_profile
        except AttributeError:
            messages.error(
                request,
                "Your student profile was not found. Please contact the administrator.",
            )
            return redirect("course_detail", pk=course.pk)

        enrolled = Enrollment.objects.filter(
            student=student,
            course=course,
            is_active=True,
        ).exists()

        if not enrolled:
            messages.error(
                request,
                "Please enroll in this course to access its lectures.",
            )
            return redirect("course_detail", pk=course.pk)

        progress, _ = LectureProgress.objects.get_or_create(
            student=student,
            lecture=lecture,
        )

    elif request.user.role not in {"teacher", "admin"}:
        messages.error(request, "You are not authorized to access this lecture.")
        return redirect("course_detail", pk=course.pk)

    return render(
        request,
        "courses/lecture.html",
        {"lecture": lecture, "progress": progress},
    )
