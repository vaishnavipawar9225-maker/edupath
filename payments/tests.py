from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Coupon

class CouponTest(TestCase):

    def test_valid_coupon(self):
        """Test that an active coupon is considered valid"""
        coupon = Coupon.objects.create(code='SAVE20', discount_percent=20, is_active=True)
        is_valid, msg = coupon.is_valid()
        
        self.assertTrue(is_valid)
        self.assertEqual(msg, "OK")

    def test_expired_coupon(self):
        """Test that a coupon past its valid_until date fails"""
        past_date = timezone.now() - timedelta(days=1)
        coupon = Coupon.objects.create(code='EXPIRED', discount_percent=50, valid_until=past_date)
        
        is_valid, msg = coupon.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(msg, "Coupon has expired")

    def test_max_uses_coupon(self):
        """Test that a coupon fails if it has reached its usage limit"""
        coupon = Coupon.objects.create(code='MAXED', discount_percent=10, max_uses=5, used_count=5)
        
        is_valid, msg = coupon.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(msg, "Coupon usage limit reached")