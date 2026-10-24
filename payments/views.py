import uuid
from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone

from courses.models import Course, Enrollment
from .models import Payment, Coupon


# ============================================================
# CHECKOUT
# ============================================================
@login_required
def checkout(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.user.role != "student":
        messages.error(request, "Only students can enroll.")
        return redirect("dashboard")

    student = request.user.student_profile

    if Enrollment.objects.filter(student=student, course=course).exists():
        messages.info(request, "You're already enrolled in this course.")
        return redirect("course_detail", pk=course.pk)

    if course.is_free or course.price == 0:
        Enrollment.objects.create(student=student, course=course)
        Payment.objects.create(
            student=student, course=course, amount=0,
            status="paid", method="mock",
            razorpay_payment_id=f"FREE_{uuid.uuid4().hex[:8]}",
        )
        messages.success(request, f"🎉 Enrolled in {course.title}!")
        return redirect("course_detail", pk=course.pk)

    has_razorpay = bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)

    if has_razorpay:
        try:
            import razorpay
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            order = client.order.create({
                "amount": int(course.price * 100),
                "currency": "INR",
                "payment_capture": 1,
            })
            Payment.objects.create(
                student=student, course=course, amount=course.price,
                razorpay_order_id=order["id"], method="upi", status="pending",
            )
            return render(request, "payments/checkout.html", {
                "order": order, "course": course,
                "razorpay_key": settings.RAZORPAY_KEY_ID,
            })
        except Exception as e:
            messages.warning(request, f"Razorpay failed ({e}). Switching to demo mode.")

    return render(request, "payments/checkout_mock.html", {
        "course": course, "student": student,
    })


# ============================================================
# APPLY COUPON (AJAX)
# ============================================================
@login_required
def apply_coupon(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    code = (request.GET.get("code") or "").strip().upper()

    if not code:
        return JsonResponse({"valid": False, "error": "Please enter a coupon code"})

    try:
        coupon = Coupon.objects.get(code__iexact=code)
    except Coupon.DoesNotExist:
        return JsonResponse({"valid": False, "error": "Invalid coupon code"})

    valid, reason = coupon.is_valid()
    if not valid:
        return JsonResponse({"valid": False, "error": reason})

    discount = (course.price * Decimal(coupon.discount_percent) / Decimal(100)).quantize(Decimal("0.01"))
    final = (course.price - discount).quantize(Decimal("0.01"))

    return JsonResponse({
        "valid": True,
        "code": coupon.code,
        "discount_percent": coupon.discount_percent,
        "discount": float(discount),
        "final": float(final),
    })


# ============================================================
# MOCK PAYMENT — CONFIRM
# ============================================================
@login_required
def mock_payment_confirm(request, course_id):
    if request.method != "POST":
        return redirect("checkout", course_id=course_id)

    course = get_object_or_404(Course, pk=course_id)
    if request.user.role != "student":
        return redirect("dashboard")

    student = request.user.student_profile
    method = request.POST.get("method", "upi")
    coupon_code = (request.POST.get("coupon_code") or "").strip().upper()

    if Enrollment.objects.filter(student=student, course=course).exists():
        payment = Payment.objects.filter(
            student=student, course=course, status="paid"
        ).first()
        return render(request, "payments/success.html", {"payment": payment})

    # Coupon validation
    coupon = None
    discount = Decimal("0.00")
    final = course.price

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code)
            valid, _ = coupon.is_valid()
            if valid:
                discount = (course.price * Decimal(coupon.discount_percent) / Decimal(100)).quantize(Decimal("0.01"))
                final = (course.price - discount).quantize(Decimal("0.01"))
            else:
                coupon = None
        except Coupon.DoesNotExist:
            coupon = None

    payment = Payment.objects.create(
        student=student,
        course=course,
        amount=final,
        discount_amount=discount,
        coupon=coupon,
        method=method,
        status="paid",
        razorpay_payment_id=f"MOCK_{method.upper()}_{uuid.uuid4().hex[:10].upper()}",
    )
    Enrollment.objects.create(student=student, course=course)

    if coupon:
        coupon.used_count = models_count_inc(coupon)
        coupon.save()

    return render(request, "payments/success.html", {"payment": payment})


def models_count_inc(coupon):
    return coupon.used_count + 1


# ============================================================
# REAL RAZORPAY CALLBACK
# ============================================================
@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        import razorpay
        data = request.POST.dict()
        try:
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            client.utility.verify_payment_signature({
                "razorpay_order_id": data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature": data["razorpay_signature"],
            })
            payment = Payment.objects.get(razorpay_order_id=data["razorpay_order_id"])
            payment.status = "paid"
            payment.razorpay_payment_id = data["razorpay_payment_id"]
            payment.save()
            Enrollment.objects.get_or_create(
                student=payment.student, course=payment.course
            )
            return render(request, "payments/success.html", {"payment": payment})
        except Exception as e:
            return render(request, "payments/failure.html", {"error": str(e)})
    return redirect("home")


# ============================================================
# PAYMENT HISTORY
# ============================================================
@login_required
def payment_history(request):
    if request.user.role != "student":
        return redirect("dashboard")

    payments = (
        Payment.objects
        .filter(student=request.user.student_profile)
        .select_related("course", "coupon")
        .order_by("-created_at")
    )
    total_paid = sum(p.amount for p in payments if p.status == "paid")
    total_saved = sum(p.discount_amount for p in payments if p.status == "paid")

    return render(request, "payments/history.html", {
        "payments": payments,
        "total_paid": total_paid,
        "total_saved": total_saved,
    })


# ============================================================
# DOWNLOAD PDF RECEIPT
# ============================================================
@login_required
def download_receipt(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)

    # Only owner or admin can download
    if request.user.role != "admin" and payment.student.user_id != request.user.id:
        messages.error(request, "You cannot access this receipt.")
        return redirect("dashboard")

    pdf = _build_receipt_pdf(payment)
    filename = f"EduPath_Receipt_{payment.razorpay_payment_id[:16] or payment.pk}.pdf"

    return FileResponse(pdf, as_attachment=True, filename=filename)


def _build_receipt_pdf(payment):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=2*cm, rightMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    purple = colors.HexColor("#5B21B6")
    gray = colors.HexColor("#64748B")

    title_style = ParagraphStyle("T", parent=styles["Heading1"],
                                  fontSize=22, textColor=purple, spaceAfter=4)
    sub_style = ParagraphStyle("S", parent=styles["Normal"],
                                fontSize=10, textColor=gray, spaceAfter=20)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
                               fontSize=13, textColor=purple, spaceAfter=8)

    elements = []

    # Header
    elements.append(Paragraph("🎓 EduPath", title_style))
    elements.append(Paragraph("Online Learning Platform for Classes 5–10", sub_style))
    elements.append(Paragraph("PAYMENT RECEIPT", h2_style))
    elements.append(Spacer(1, 0.3*cm))

    # Receipt info
    receipt_data = [
        ["Transaction ID:", payment.razorpay_payment_id or "—"],
        ["Date:", payment.created_at.strftime("%d %B %Y, %H:%M IST")],
        ["Status:", payment.get_status_display()],
    ]
    receipt_table = Table(receipt_data, colWidths=[4*cm, 12*cm])
    receipt_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), gray),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(receipt_table)
    elements.append(Spacer(1, 0.5*cm))

    # Student info
    elements.append(Paragraph("Billed To", h2_style))
    student_data = [
        ["Student:", payment.student.user.get_full_name() or payment.student.user.username],
        ["Class:", f"Class {payment.student.grade}"],
        ["Email:", payment.student.user.email or "—"],
    ]
    student_table = Table(student_data, colWidths=[4*cm, 12*cm])
    student_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), gray),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 0.5*cm))

    # Line items
    elements.append(Paragraph("Course Details", h2_style))
    line_items = [
        ["Course", "Price"],
        [payment.course.title, f"₹{payment.original_amount()}"],
    ]
    if payment.discount_amount and payment.discount_amount > 0:
        coupon_label = f"Coupon ({payment.coupon.code if payment.coupon else 'Applied'})"
        line_items.append([coupon_label, f"− ₹{payment.discount_amount}"])
    line_items.append(["Total Paid", f"₹{payment.amount}"])

    items_table = Table(line_items, colWidths=[13*cm, 3*cm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), purple),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F8FAFC")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EDE9FE")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, -1), (-1, -1), purple),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 1*cm))

    # Footer
    footer_style = ParagraphStyle("F", parent=styles["Normal"],
                                   fontSize=9, textColor=gray, alignment=1)
    elements.append(Paragraph(
        "This is a computer-generated receipt. For queries, contact hello@edupath.in",
        footer_style,
    ))
    elements.append(Paragraph("© 2026 EduPath. All rights reserved.", footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ============================================================
# REFUND (Admin only)
# ============================================================
@login_required
def refund_payment(request, payment_id):
    if request.user.role != "admin":
        messages.error(request, "Only admins can issue refunds.")
        return redirect("dashboard")

    payment = get_object_or_404(Payment, pk=payment_id)

    if payment.status != "paid":
        messages.warning(request, "Only paid transactions can be refunded.")
        return redirect("payment_history")

    # Mark refunded + remove enrollment
    payment.status = "refunded"
    payment.save()
    Enrollment.objects.filter(
        student=payment.student, course=payment.course
    ).delete()

    messages.success(
        request,
        f"✅ Refund issued for ₹{payment.amount} — enrollment removed."
    )
    return redirect("payment_history")