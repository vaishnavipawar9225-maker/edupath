from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment

@receiver(pre_save, sender=Payment)
def track_payment(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_status = Payment.objects.get(pk=instance.pk).status
        except Payment.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Payment)
def notify_payment(sender, instance, created, **kwargs):
    old = getattr(instance, "_old_status", None)
    if not (instance.status == "paid" and old != "paid"):
        return
    if not instance.student.user.email:
        return
    send_mail(
        subject=f"✅ Payment Confirmed — {instance.course.title}",
        message=f"Hi {instance.student.user.username},\n\n"
                f"Payment successful. You now have access to '{instance.course.title}'.\n"
                f"Amount: ₹{instance.amount}\n",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[instance.student.user.email],
        fail_silently=True,
    )