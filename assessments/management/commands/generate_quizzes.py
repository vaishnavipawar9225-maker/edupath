import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from assessments.models import Quiz, Question, Choice, QuizAttempt
from assessments.quiz_generator import generate_questions_for_quiz
from accounts.models import StudentProfile


class Command(BaseCommand):
    help = "Regenerate every quiz with FRESH randomly-generated topic-specific questions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--quiz", type=str, default=None,
            help="Regenerate only one quiz by title (e.g. 'Algebra Quiz 1')"
        )
        parser.add_argument(
            "--keep-attempts", action="store_true",
            help="Keep existing quiz attempts (default: delete and re-create)"
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("\n🤖 Generating dynamic quizzes...\n"))

        quizzes = Quiz.objects.all()
        if options["quiz"]:
            quizzes = quizzes.filter(title__iexact=options["quiz"])
            if not quizzes.exists():
                self.stdout.write(self.style.ERROR(f"❌ Quiz not found: {options['quiz']}"))
                return

        total_q = 0
        total_choices = 0

        for quiz in quizzes:
            # Wipe old
            old_count = quiz.questions.count()
            quiz.questions.all().delete()
            if not options["keep_attempts"]:
                quiz.quizattempt_set.all().delete()

            # Generate fresh
            generated = generate_questions_for_quiz(quiz, n=5)
            marks_total = 0

            for text, choices, correct_idx, marks in generated:
                q = Question.objects.create(quiz=quiz, text=text, marks=marks)
                for i, c_text in enumerate(choices):
                    Choice.objects.create(
                        question=q, text=c_text, is_correct=(i == correct_idx)
                    )
                marks_total += marks
                total_q += 1
                total_choices += 4

            quiz.total_marks = marks_total
            quiz.is_published = True
            quiz.save()

            self.stdout.write(self.style.SUCCESS(
                f"  ✅ {quiz.title}: {len(generated)} fresh questions ({marks_total} marks) "
                f"[replaced {old_count}]"
            ))

        # Re-populate student attempts for parent dashboard
        if not options["keep_attempts"]:
            attempts = 0
            for student in StudentProfile.objects.all()[:4]:
                for quiz in Quiz.objects.filter(is_published=True)[:3]:
                    score = random.randint(max(4, quiz.total_marks // 2), quiz.total_marks)
                    QuizAttempt.objects.create(
                        student=student, quiz=quiz, score=score,
                        completed_at=timezone.now() - timedelta(days=random.randint(1, 10)),
                    )
                    attempts += 1
            self.stdout.write(self.style.SUCCESS(
                f"\n  📊 {attempts} quiz attempts re-created for parent dashboard"
            ))

        self.stdout.write("\n" + "=" * 62)
        self.stdout.write(self.style.SUCCESS("🎉 ALL QUIZZES REGENERATED!"))
        self.stdout.write(f"   Total questions : {total_q}")
        self.stdout.write(f"   Total choices   : {total_choices}")
        self.stdout.write("=" * 62 + "\n")