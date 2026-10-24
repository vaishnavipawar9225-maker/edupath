from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Quiz
from courses.models import Enrollment

@receiver(pre_save, sender=Quiz)
def track_quiz_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_is_published = Quiz.objects.get(pk=instance.pk).is_published
        except Quiz.DoesNotExist:
            instance._old_is_published = False
    else:
        instance._old_is_published = False

@receiver(post_save, sender=Quiz)
def notify_quiz_published(sender, instance, created, **kwargs):
    old = getattr(instance, "_old_is_published", False)
    if not (instance.is_published and not old):
        return
    enrollments = Enrollment.objects.filter(course=instance.course, is_active=True).select_related("student__user")
    recipients = [e.student.user.email for e in enrollments if e.student.user.email]
    if not recipients:
        return
    send_mail(
        subject=f"🔔 New Quiz Published: {instance.title}",
        message=f"New quiz '{instance.title}' in '{instance.course.title}'.\n"
                f"Duration: {instance.duration_minutes} min. Total Marks: {instance.total_marks}.\n"
                f"Attempt: http://127.0.0.1:8000/quiz/start/{instance.pk}/",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=True,
    )