from django.db import models
from django.utils import timezone
from accounts.models import StudentProfile
from courses.models import Course


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    discount_percent = models.PositiveIntegerField(default=10, help_text="1–100")
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    used_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% off)"

    def is_valid(self):
        if not self.is_active:
            return False, "Coupon is disabled"
        if self.valid_until and self.valid_until < timezone.now():
            return False, "Coupon has expired"
        if self.max_uses and self.used_count >= self.max_uses:
            return False, "Coupon usage limit reached"
        return True, "OK"


class Payment(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]
    METHOD_CHOICES = [
        ("upi", "UPI / Google Pay / PhonePe"),
        ("card", "Credit / Debit Card"),
        ("netbanking", "Net Banking"),
        ("wallet", "Wallet"),
        ("mock", "Mock (Dev Mode)"),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2, help_text="Final amount paid")
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="mock")
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def original_amount(self):
        return self.amount + self.discount_amount

    def __str__(self):
        return f"{self.student} - {self.course.title} - ₹{self.amount} ({self.status})"