import json
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from courses.models import Course, Enrollment
from assessments.models import QuizAttempt
from attendance.models import Attendance
from payments.models import Payment
from .forms import MeetingRequestForm
from liveclasses.models import ParentMeeting
from django.contrib import messages
from accounts.models import User
from .forms import LinkChildForm

from django.shortcuts import get_object_or_404
from liveclasses.models import ParentMeeting
from .models import Notification
from accounts.models import StudentProfile
from .forms import MeetingForm
from liveclasses.models import LiveClass
from .models import Notification
from courses.models import Enrollment
from django.urls import reverse
from liveclasses.models import LiveClass, ParentMeeting

def home(request):
    featured = Course.objects.all()[:6]
    return render(request, "home.html", {"featured": featured})

@login_required
def dashboard(request):
    role = request.user.role
    if role == "student": return student_dashboard(request)
    if role == "teacher": return teacher_dashboard(request)
    if role == "parent": return parent_dashboard(request)
    return admin_dashboard(request) 

    student = request.user.student_profile
    enrollments = Enrollment.objects.filter(student=student).select_related("course")
    attempts = QuizAttempt.objects.filter(student=student).order_by("-started_at")[:5]
    attendance = Attendance.objects.filter(student=student)
    total = attendance.count()
    present = attendance.filter(status="present").count()
    pct = round((present / total * 100) if total else 0, 1)
    return render(request, "dashboard/student.html", {
        "enrollments": enrollments, "attempts": attempts, "attendance_percent": pct,
    })
def student_dashboard(request):
    student = request.user.student_profile
    # Fetch ONLY the courses this student is enrolled in
    enrollments = Enrollment.objects.filter(student=student).select_related("course")
    
    attempts = QuizAttempt.objects.filter(student=student).order_by("-started_at")[:5]
    attendance = Attendance.objects.filter(student=student)
    total = attendance.count()
    present = attendance.filter(status="present").count()
    pct = round((present / total * 100) if total else 0, 1)
    
    return render(request, "dashboard/student.html", {
        "enrollments": enrollments, 
        "attempts": attempts, 
        "attendance_percent": pct,
    })
    
    
def teacher_dashboard(request):
    from liveclasses.models import ParentMeeting
    courses = Course.objects.filter(teacher=request.user)
    # Fetch meetings requested for this specific teacher
    meetings = ParentMeeting.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request, "dashboard/teacher.html", {"courses": courses, "meetings": meetings})

def parent_dashboard(request):
    from accounts.models import StudentProfile

    profiles = (
        StudentProfile.objects
        .filter(parent=request.user)
        .select_related("user")
    )
    child_data = []

    for profile in profiles:
        child = profile.user

        attempts = QuizAttempt.objects.filter(student=profile).order_by("-started_at")
        attendance = Attendance.objects.filter(student=profile)

        total   = attendance.count()
        present = attendance.filter(status="present").count()
        absent  = attendance.filter(status="absent").count()
        late    = attendance.filter(status="late").count()
        pct = round((present / total * 100) if total else 0, 1)

        recent = list(attempts[:6])[::-1]
        child_data.append({
            "child": child,
            "profile": profile,
            "enrollments": Enrollment.objects.filter(student=profile).count(),
            "attempts": attempts[:5],
            "attendance_percent": pct,
            "quiz_labels": json.dumps([a.quiz.title[:22] for a in recent]),
            "quiz_percentages": json.dumps([a.percentage() for a in recent]),
            "attendance_present": present,
            "attendance_absent":  absent,
            "attendance_late":    late,
        })

    return render(request, "dashboard/parent.html", {"child_data": child_data})


@login_required
def parent_meetings(request):
    if request.user.role != 'parent':
        return redirect('dashboard')
    
    # 1. Fetch PTM requests
    meetings = ParentMeeting.objects.filter(parent=request.user).order_by('-created_at')
    
    # 2. Fetch Live Classes scheduled by teachers for their children
    # Get the children linked to this parent
    children = request.user.children.all()
    child_courses = []
    for child in children:
        # Get all courses the child is enrolled in
        enrollments = Enrollment.objects.filter(student=child, is_active=True)
        for e in enrollments:
            child_courses.append(e.course.id)

    # Fetch upcoming live classes for those courses
    live_classes = LiveClass.objects.filter(course_id__in=child_courses).order_by('scheduled_at')
    
    return render(request, "dashboard/meetings.html", {
        "meetings": meetings,
        "live_classes": live_classes
    })
    
@login_required
def request_meeting(request):
    if request.user.role != 'parent':
        return redirect('dashboard')

    if request.method == "POST":
        form = MeetingRequestForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.parent = request.user
            meeting.save()
            messages.success(request, "✅ Meeting request sent successfully!") 
            return redirect('parent_meetings')
    else:
        form = MeetingRequestForm()

    return render(request, "dashboard/request_meeting.html", {"form": form})


def admin_dashboard(request):
    # Fetch recent data for the admin to see
    recent_payments = Payment.objects.filter(status="paid").select_related("student__user", "course").order_by("-created_at")[:5]
    recent_enrollments = Enrollment.objects.select_related("student__user", "course").order_by("-enrolled_at")[:5]
    
    context = {
        "total_courses": Course.objects.count(),
        "total_enrollments": Enrollment.objects.count(),
        "total_payments": Payment.objects.filter(status="paid").count(),
        "total_users": User.objects.count(),
        "recent_payments": recent_payments,
        "recent_enrollments": recent_enrollments,
    }
    return render(request, "dashboard/admin.html", context)

@login_required
def link_child(request):
    if request.user.role != 'parent':
        return redirect('dashboard')

    if request.method == "POST":
        form = LinkChildForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['student_email']
            try:
                # Find the student by email
                student_user = User.objects.get(email=email, role='student')
                profile = student_user.student_profile
                
                # Check if they are already linked
                if profile.parent:
                    messages.error(request, "This student is already linked to a parent.")
                else:
                    profile.parent = request.user
                    profile.save()
                    messages.success(request, f"✅ Successfully linked {student_user.get_full_name() or student_user.username} to your account!")
                    return redirect('dashboard')
            except User.DoesNotExist:
                messages.error(request, "❌ No student found with that email address.")
            except Exception as e:
                messages.error(request, "An error occurred while linking the student.")
    else:
        form = LinkChildForm()

    return render(request, "dashboard/link_child.html", {"form": form})

@login_required
def update_meeting_status(request, meeting_id, status):
    if request.user.role != 'teacher':
        return redirect('dashboard')
        
    meeting = get_object_or_404(ParentMeeting, id=meeting_id, teacher=request.user)
    
    if status in ['approved', 'rejected']:
        meeting.status = status
        meeting.save()
        messages.success(request, f"Meeting successfully {status}!")
        
    return redirect('dashboard')

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    # Mark all as read
    notifications.update(is_read=True)
    return render(request, "dashboard/notifications.html", {"notifications": notifications})

@login_required
def send_teacher_notification(request, course_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')
        
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        
        # Send to all enrolled students
        enrollments = course.enrollments.filter(is_active=True)
        for e in enrollments:
            Notification.objects.create(recipient=e.student.user, title=title, message=message)
            # Optional: Send email here
            
        messages.success(request, f"Notification sent to {enrollments.count()} students!")
        return redirect('dashboard')
        
    return render(request, "dashboard/send_notification.html", {"course": course})

@login_required
def create_meeting(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')

    if request.method == 'POST':
        form = MeetingForm(request.POST, teacher=request.user)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.teacher = request.user
            meeting.save()
            
            # 🔔 Generate the URL to join this specific meeting
            # This uses the 'join_class' URL from your liveclasses app
            meeting_url = reverse('join_class', args=[meeting.id])

            # 🔔 Send Notifications to Students and Parents
            enrollments = Enrollment.objects.filter(course=meeting.course, is_active=True)
            notif_count = 0
            
            for e in enrollments:
                # 1. Notify Student
                Notification.objects.create(
                    recipient=e.student.user,
                    title=f"📅 New Meeting: {meeting.title}",
                    message=f"A new meeting for {meeting.course.title} has been scheduled on {meeting.scheduled_at.strftime('%d %b %Y, %I:%M %p')}. Please join on time.",
                    link=meeting_url
                )
                notif_count += 1
                
                # 2. Notify Parent (if linked)
                if e.student.parent:
                    Notification.objects.create(
                        recipient=e.student.parent,
                        title=f"📅 Meeting Scheduled for {e.student.user.username}",
                        message=f"Teacher {request.user.username} scheduled a meeting for {meeting.course.title} on {meeting.scheduled_at.strftime('%d %b %Y, %I:%M %p')}.",
                        link=meeting_url
                    )
                    notif_count += 1

            messages.success(request, f"✅ Meeting scheduled! Sent {notif_count} notifications.")
            return redirect('dashboard')
    else:
        form = MeetingForm(teacher=request.user)

    return render(request, 'dashboard/create_meeting.html', {'form': form})