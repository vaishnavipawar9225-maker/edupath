from django.contrib import admin
from .models import Payment, Coupon # <-- Make sure Coupon is imported

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "amount", "status", "created_at")
    list_filter = ("status",)

# Register the Coupon model
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "is_active", "valid_until", "used_count", "max_uses")
    list_filter = ("is_active",)
    search_fields = ("code",)