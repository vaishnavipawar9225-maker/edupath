from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from payments.models import Coupon


class Command(BaseCommand):
    help = "Create demo coupon codes"

    def handle(self, *args, **options):
        coupons = [
            ("SAVE10", 10, 100),
            ("SAVE20", 20, 100),
            ("WELCOME50", 50, 50),
            ("FIRST50", 50, 10),
            ("DEMO100", 100, 999),  # 100% off for full demo
        ]
        for code, pct, max_uses in coupons:
            c, created = Coupon.objects.get_or_create(
                code=code,
                defaults={
                    "discount_percent": pct,
                    "max_uses": max_uses,
                    "is_active": True,
                    "valid_until": timezone.now() + timedelta(days=90),
                },
            )
            status = "✅ Created" if created else "⏭️  Exists"
            self.stdout.write(f"{status}: {c.code} — {c.discount_percent}% off (max {c.max_uses} uses)")

        self.stdout.write(self.style.SUCCESS("\n🎟️  Demo coupons ready!"))
        self.stdout.write("\nTry these at checkout:")
        self.stdout.write("  SAVE10      → 10% off")
        self.stdout.write("  SAVE20      → 20% off")
        self.stdout.write("  WELCOME50   → 50% off")
        self.stdout.write("  DEMO100     → 100% off (free!)")