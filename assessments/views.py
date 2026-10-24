
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone

from courses.models import Enrollment
from .models import Quiz, Question, Choice, QuizAttempt, StudentAnswer
from django.contrib import messages
from django.core.management import call_command
from django.contrib import messages
from django.core.management import call_command
from .forms import QuizCreateForm
from .quiz_generator import generate_questions_for_quiz
from django.db import transaction


def get_student_profile(request):
    """Return the student's profile, or None for other account roles."""
    if not request.user.is_authenticated or request.user.role != "student":
        return None

    try:
        return request.user.student_profile
    except Exception:
        return None
    
@login_required
def regenerate_quiz_questions(request, pk):
    """Teacher/admin can regenerate questions on-demand from the UI."""
    if request.user.role not in ("teacher", "admin"):
        messages.error(request, "Only teachers can regenerate quizzes.")
        return redirect("quiz_list")

    try:
        call_command("generate_quizzes", quiz=Quiz.objects.get(pk=pk).title)
        messages.success(request, "🔄 Fresh questions generated!")
    except Exception as e:
        messages.error(request, f"Failed: {e}")

    return redirect("quiz_list")


@login_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(is_published=True)
    course_id = request.GET.get("course")
    if course_id:
        quizzes = quizzes.filter(course_id=course_id)
        
    # NEW: Find out which quizzes this student has already completed
    attempted_quiz_ids = []
    if request.user.role == "student":
        attempted_quiz_ids = list(QuizAttempt.objects.filter(
            student=request.user.student_profile,
            completed_at__isnull=False  # Only count finished quizzes
        ).values_list('quiz_id', flat=True))

    return render(request, "assessments/list.html", {
        "quizzes": quizzes,
        "attempted_quiz_ids": attempted_quiz_ids,
    })


@login_required
def start_quiz(request, pk):
    student = get_student_profile(request)

    if student is None:
        messages.error(request, "Only students can take quizzes.")
        return redirect("dashboard")

    quiz = get_object_or_404(
        Quiz.objects.select_related("course"),
        pk=pk,
        is_published=True,
        course__enrollments__student=student,
        course__enrollments__is_active=True,
    )

    # Reuse an unfinished attempt if the student refreshes or returns.
    attempt = QuizAttempt.objects.filter(
        student=student,
        quiz=quiz,
        completed_at__isnull=True,
    ).order_by("-started_at").first()

    if attempt is None:
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
        )

    questions = quiz.questions.prefetch_related("choices").all()

    return render(request, "assessments/take.html", {
        "quiz": quiz,
        "attempt": attempt,
        "questions": questions,
    })
    


@login_required
def teacher_quiz_list(request):
    """Dashboard for teachers — list all quizzes in their courses."""
    if request.user.role not in ("teacher", "admin"):
        messages.error(request, "Teachers only.")
        return redirect("dashboard")

    if request.user.role == "admin":
        quizzes = Quiz.objects.all().select_related("course", "course__subject")
    else:
        quizzes = Quiz.objects.filter(
            course__teacher=request.user
        ).select_related("course", "course__subject")

    stats = {
        "total_quizzes": quizzes.count(),
        "published": quizzes.filter(is_published=True).count(),
        "total_attempts": sum(q.quizattempt_set.count() for q in quizzes),
    }
    return render(request, "assessments/teacher_list.html", {
        "quizzes": quizzes, "stats": stats,
    })

@login_required
def teacher_create_quiz(request):
    if request.user.role not in ("teacher", "admin"):
        return redirect("dashboard")

    if request.method == "POST":
        form = QuizCreateForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    quiz = form.save(commit=False)
                    quiz.is_published = True
                    quiz.save()

                    n = form.cleaned_data["num_questions"]
                    generated = generate_questions_for_quiz(quiz, n=n)

                    total_marks = 0
                    for text, choices, correct_idx, marks in generated:
                        q = Question.objects.create(quiz=quiz, text=text, marks=marks)
                        for i, c_text in enumerate(choices):
                            Choice.objects.create(
                                question=q, text=c_text, is_correct=(i == correct_idx)
                            )
                        total_marks += marks

                    quiz.total_marks = total_marks
                    quiz.save()

                messages.success(
                    request,
                    f"✅ Quiz '{quiz.title}' created with {len(generated)} questions!"
                )
                return redirect("teacher_quiz_detail", pk=quiz.pk)

            except Exception as e:
                messages.error(request, f"❌ Failed to create quiz: {e}")
                return redirect("teacher_quiz_list")
    else:
        form = QuizCreateForm(user=request.user)

    return render(request, "assessments/teacher_create.html", {"form": form})


@login_required
def teacher_quiz_detail(request, pk):
    """Teacher views one quiz + all student attempts."""
    if request.user.role not in ("teacher", "admin"):
        return redirect("dashboard")

    quiz = get_object_or_404(Quiz, pk=pk)
    if request.user.role == "teacher" and quiz.course.teacher != request.user:
        messages.error(request, "You don't own this quiz.")
        return redirect("teacher_quiz_list")

    questions = quiz.questions.prefetch_related("choices").all()
    attempts = quiz.quizattempt_set.select_related("student__user").order_by("-started_at")

    avg = 0
    if attempts:
        avg = round(sum(a.score for a in attempts) / len(attempts), 1)

    return render(request, "assessments/teacher_detail.html", {
        "quiz": quiz, "questions": questions, "attempts": attempts, "avg_score": avg,
    })


@login_required
def teacher_regenerate_quiz(request, pk):
    """Regenerate questions for a quiz — teacher only."""
    if request.user.role not in ("teacher", "admin"):
        return redirect("dashboard")

    quiz = get_object_or_404(Quiz, pk=pk)
    if request.user.role == "teacher" and quiz.course.teacher != request.user:
        messages.error(request, "You don't own this quiz.")
        return redirect("teacher_quiz_list")

    # Delete old questions (this cascades to choices and student answers)
    quiz.questions.all().delete()
    quiz.quizattempt_set.all().delete()

    # Generate fresh
    generated = generate_questions_for_quiz(quiz, n=5)
    total_marks = 0
    for text, choices, correct_idx, marks in generated:
        q = Question.objects.create(quiz=quiz, text=text, marks=marks)
        for i, c_text in enumerate(choices):
            Choice.objects.create(question=q, text=c_text, is_correct=(i == correct_idx))
        total_marks += marks

    quiz.total_marks = total_marks
    quiz.save()

    messages.success(request, f"🔄 '{quiz.title}' regenerated with fresh questions!")
    return redirect("teacher_quiz_detail", pk=quiz.pk)


@login_required
@require_POST
def submit_quiz(request, attempt_id):
    student = get_student_profile(request)

    if student is None:
        messages.error(request, "Only students can submit quizzes.")
        return redirect("dashboard")

    # A student cannot submit another student's attempt.
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz", "quiz__course"),
        pk=attempt_id,
        student=student,
        quiz__course__enrollments__student=student,
        quiz__course__enrollments__is_active=True,
    )

    if attempt.completed_at is not None:
        messages.info(request, "This quiz has already been submitted.")
        return redirect("quiz_result", pk=attempt.pk)

    questions = attempt.quiz.questions.prefetch_related("choices").all()

    with transaction.atomic():
        score = 0

        for question in questions:
            choice_id = request.POST.get(f"q_{question.id}")

            if not choice_id:
                continue

            # Accept only a choice belonging to this question.
            choice = Choice.objects.filter(
                pk=choice_id,
                question=question,
            ).first()

            if choice is None:
                continue

            is_correct = choice.is_correct

            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=choice,
                is_correct=is_correct,
            )

            if is_correct:
                score += question.marks

        attempt.score = score
        attempt.completed_at = timezone.now()
        attempt.save(update_fields=["score", "completed_at"])

    return redirect("quiz_result", pk=attempt.pk)


@login_required
def quiz_result(request, pk):
    student = get_student_profile(request)

    if student is None:
        messages.error(request, "Quiz results are available to students only.")
        return redirect("dashboard")

    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz", "quiz__course"),
        pk=pk,
        student=student,
        quiz__course__enrollments__student=student,
        quiz__course__enrollments__is_active=True,
    )

    if attempt.completed_at is None:
        return redirect("start_quiz", pk=attempt.quiz_id)

    answers = attempt.answers.select_related(
        "question", "selected_choice"
    ).all()

    return render(request, "assessments/result.html", {
        "attempt": attempt,
        "answers": answers,
    })
