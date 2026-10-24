from django.urls import path
from . import views

urlpatterns = [
    path("checkout/<int:course_id>/", views.checkout, name="checkout"),
    path("apply-coupon/<int:course_id>/", views.apply_coupon, name="apply_coupon"),
    path("mock-confirm/<int:course_id>/", views.mock_payment_confirm, name="mock_payment_confirm"),
    path("success/", views.payment_success, name="payment_success"),
    path("history/", views.payment_history, name="payment_history"),
    path("receipt/<int:payment_id>/", views.download_receipt, name="download_receipt"),
    path("refund/<int:payment_id>/", views.refund_payment, name="refund_payment"),
]