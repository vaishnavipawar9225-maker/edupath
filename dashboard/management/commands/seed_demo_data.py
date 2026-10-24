import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User, StudentProfile, TeacherProfile, ParentProfile
from courses.models import Subject, Course, Chapter, Lecture, Enrollment
from assessments.models import Quiz, Question, Choice, QuizAttempt
from attendance.models import Attendance
from payments.models import Payment
from liveclasses.models import LiveClass


class Command(BaseCommand):
    help = "Seed EduPath with realistic demo data (idempotent — safe to re-run)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("\n🌱 Seeding demo data...\n"))

        # ================= USERS =================
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@edupath.in", "role": "admin",
                      "is_staff": True, "is_superuser": True},
        )
        admin.set_password("admin12345")
        admin.save()

        teachers_spec = [
            ("verma",  "Amit",  "Verma",  "Mathematics, Science"),
            ("sharma", "Priya", "Sharma", "English, Hindi"),
            ("khan",   "Imran", "Khan",   "Physics, Chemistry"),
        ]
        teachers = []
        for un, fn, ln, subs in teachers_spec:
            t, _ = User.objects.get_or_create(
                username=un,
                defaults={"email": f"{un}@edupath.in", "role": "teacher",
                          "first_name": fn, "last_name": ln},
            )
            t.set_password("pass12345"); t.save()
            tp, _ = TeacherProfile.objects.get_or_create(user=t)
            tp.subjects = subs
            tp.bio = f"10+ years teaching {subs} for Classes 5–10."
            tp.experience_years = 10
            tp.save()
            teachers.append(t)

        parent, _ = User.objects.get_or_create(
            username="parent1",
            defaults={"email": "parent@edupath.in", "role": "parent",
                      "first_name": "Rajesh", "last_name": "Sharma"},
        )
        parent.set_password("pass12345"); parent.save()
        ParentProfile.objects.get_or_create(user=parent)

        students_spec = [
            ("riya",  "Riya",  "Sharma", 10),
            ("arjun", "Arjun", "Kumar",   9),
            ("priya", "Priya", "Patel",   8),
            ("rohan", "Rohan", "Gupta",   7),
        ]
        students = []
        for un, fn, ln, grade in students_spec:
            s, _ = User.objects.get_or_create(
                username=un,
                defaults={"email": f"{un}@edupath.in", "role": "student",
                          "first_name": fn, "last_name": ln},
            )
            s.set_password("pass12345"); s.save()
            sp, created = StudentProfile.objects.get_or_create(
                user=s, defaults={"grade": grade, "parent": parent},
            )
            if not created:
                sp.grade, sp.parent = grade, parent
                sp.save()
            students.append(s)

        self.stdout.write(self.style.SUCCESS(
            f"✅ Users: 1 admin, {len(teachers)} teachers, {len(students)} students, 1 parent"))

        # ================= SUBJECTS =================
        subjects_spec = [
            ("Mathematics", 5), ("English", 5), ("Science", 5),
            ("Mathematics", 6), ("English", 6), ("Science", 6),
            ("Mathematics", 7), ("Science", 7), ("English", 7),
            ("Mathematics", 8), ("Science", 8), ("English", 8),
            ("Mathematics", 9), ("Science", 9), ("English", 9),
            ("Mathematics", 10), ("Science", 10), ("English", 10),
        ]
        subjects = {}
        for name, grade in subjects_spec:
            subj, _ = Subject.objects.get_or_create(name=name, grade=grade)
            subjects[(name, grade)] = subj
        self.stdout.write(self.style.SUCCESS(f"✅ Subjects: {len(subjects)}"))

        # ================= COURSES =================
        courses_spec = [
            ("Algebra Mastery",      "Mathematics", 10, 499, "Polynomials, quadratic equations, and word problems with 40+ video lectures.", teachers[0]),
            ("Physics Fundamentals", "Science",     10, 399, "Motion, force, gravitation, and light explained with real-world examples.", teachers[2]),
            ("English Grammar Pro",  "English",     10,   0, "Tenses, voice, and comprehension practice with daily drills.", teachers[1]),
            ("Geometry Essentials",  "Mathematics",  9, 349, "Triangles, circles, and coordinate geometry — step by step.", teachers[0]),
            ("Biology Basics",       "Science",      9, 299, "Cells, tissues, and life processes in plants and animals.", teachers[2]),
            ("Number Magic",         "Mathematics",  8,   0, "Fractions, decimals, and integers made easy.", teachers[0]),
            ("Chemical Reactions",   "Science",      8, 249, "Acids, bases, and salts with hands-on experiments.", teachers[2]),
            ("Grammar Wizard",       "English",      7, 199, "Sentence structure, punctuation, and creative writing.", teachers[1]),
            ("Life Processes",       "Science",      7, 249, "Nutrition, respiration, and transportation in living beings.", teachers[2]),
            ("Fractions & Decimals", "Mathematics",  6,   0, "Master fractions, decimals, and percentage conversions.", teachers[0]),
            ("Everyday Science",     "Science",      5, 149, "Simple machines, plants, and the human body.", teachers[2]),
            ("English Stories",      "English",      5,   0, "Reading comprehension and story writing for young learners.", teachers[1]),
        ]
        courses = []
        for title, subj_name, grade, price, desc, teacher in courses_spec:
            c, _ = Course.objects.get_or_create(
                title=title,
                defaults={
                    "subject": subjects[(subj_name, grade)],
                    "teacher": teacher,
                    "description": desc,
                    "price": price,
                    "is_free": price == 0,
                },
            )
            courses.append(c)
        self.stdout.write(self.style.SUCCESS(f"✅ Courses: {len(courses)}"))

        # ================= CHAPTERS + LECTURES =================
        videos = [
            "https://www.youtube.com/embed/WUvTyaaNkzM",
            "https://www.youtube.com/embed/8mAITcNt710",
            "https://www.youtube.com/embed/Y1B0gDF5q5Y",
        ]
        chapter_titles = ["Introduction", "Core Concepts", "Advanced Topics", "Practice Problems"]

        for course in courses[:8]:
            for i, ctitle in enumerate(chapter_titles, start=1):
                chapter, _ = Chapter.objects.get_or_create(
                    course=course,
                    title=f"Chapter {i} — {ctitle}",
                    defaults={"order": i},
                )
                for j in range(1, 3):
                    Lecture.objects.get_or_create(
                        chapter=chapter,
                        title=f"Lecture {j} — {'Basics' if j == 1 else 'Practice Session'}",
                        defaults={
                            "video_url": random.choice(videos),
                            "duration_minutes": random.randint(12, 25),
                            "order": j,
                        },
                    )
        self.stdout.write(self.style.SUCCESS("✅ Chapters and lectures added"))

        # ================= ENROLLMENTS + PAYMENTS =================
        enroll_count = 0
        for student in students:
            for course in courses[:4]:
                _, created = Enrollment.objects.get_or_create(
                    student=student.student_profile, course=course,
                )
                if created:
                    enroll_count += 1
                Payment.objects.get_or_create(
                    student=student.student_profile,
                    course=course,
                    defaults={
                        "amount": course.price,
                        "status": "paid",
                        "razorpay_payment_id": f"pay_demo_{student.id}_{course.id}",
                    },
                )
        self.stdout.write(self.style.SUCCESS(f"✅ Enrollments: {enroll_count}"))

        # ================= QUIZZES =================
        quiz_spec = [
            ("Algebra Quiz 1",  courses[0]),
            ("Physics Quiz 1",  courses[1]),
            ("Grammar Quiz 1",  courses[2]),
        ]
        question_bank = [
            ("What is 2 + 2?",                  ["3", "4", "5", "6"],           1),
            ("What is 5 × 3?",                  ["10", "12", "15", "18"],       2),
            ("What is the square root of 16?",  ["2", "3", "4", "5"],           2),
            ("Solve: 3x = 9. What is x?",       ["1", "2", "3", "9"],           2),
            ("Which is a prime number?",        ["4", "6", "9", "7"],           3),
        ]
        for q_title, q_course in quiz_spec:
            quiz, created = Quiz.objects.get_or_create(
                course=q_course, title=q_title,
                defaults={"duration_minutes": 15, "is_published": True},
            )
            if created:
                total = 0
                for q_text, choices, correct_idx in question_bank:
                    q = Question.objects.create(quiz=quiz, text=q_text, marks=2)
                    for idx, choice_text in enumerate(choices):
                        Choice.objects.create(
                            question=q, text=choice_text,
                            is_correct=(idx == correct_idx),
                        )
                    total += 2
                quiz.total_marks = total
                quiz.save()
        self.stdout.write(self.style.SUCCESS("✅ 3 published quizzes with questions"))

        # ================= QUIZ ATTEMPTS (for parent dashboard chart) =================
        attempts_count = 0
        for student in students[:3]:
            for quiz in Quiz.objects.all()[:3]:
                # Check if ANY attempt exists first, bypassing get_or_create's strictness
                if not QuizAttempt.objects.filter(student=student.student_profile, quiz=quiz).exists():
                    QuizAttempt.objects.create(
                        student=student.student_profile, quiz=quiz,
                        score=random.randint(max(3, quiz.total_marks // 2), quiz.total_marks),
                        completed_at=timezone.now() - timedelta(days=random.randint(1, 10)),
                    )
                    attempts_count += 1
        self.stdout.write(self.style.SUCCESS(f"✅ Quiz attempts: {attempts_count}"))

        # ================= ATTENDANCE =================
        attendance_count = 0
        today = timezone.now().date()
        for student in students:
            for course in courses[:2]:
                for days_ago in range(1, 12):
                    date = today - timedelta(days=days_ago)
                    if date.weekday() >= 5:
                        continue
                    status = random.choices(
                        ["present", "absent", "late"], weights=[85, 10, 5],
                    )[0]
                    _, created = Attendance.objects.get_or_create(
                        student=student.student_profile,
                        course=course, date=date,
                        defaults={"status": status, "marked_by": course.teacher},
                    )
                    if created:
                        attendance_count += 1
        self.stdout.write(self.style.SUCCESS(f"✅ Attendance records: {attendance_count}"))

        # ================= LIVE CLASSES =================
        for i, course in enumerate(courses[:3], start=1):
            LiveClass.objects.get_or_create(
                course=course,
                title=f"Live Session {i}",
                defaults={
                    "scheduled_at": timezone.now() + timedelta(hours=i * 4),
                    "duration_minutes": 60,
                    "teacher": course.teacher,
                },
            )
        self.stdout.write(self.style.SUCCESS("✅ 3 live classes scheduled"))

        # ================= SUMMARY =================
        self.stdout.write("\n" + "=" * 62)
        self.stdout.write(self.style.SUCCESS("🎉  DEMO DATA SEEDED SUCCESSFULLY!"))
        self.stdout.write("=" * 62)
        self.stdout.write("\n📋 LOGIN CREDENTIALS")
        self.stdout.write("   Admin   →  admin    / admin12345")
        self.stdout.write("   Teacher →  verma    / pass12345")
        self.stdout.write("   Student →  riya     / pass12345")
        self.stdout.write("   Parent  →  parent1  / pass12345")
        self.stdout.write("\n🌐 Open: http://127.0.0.1:8000/")
        self.stdout.write("=" * 62 + "\n")