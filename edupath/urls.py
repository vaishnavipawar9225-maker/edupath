from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import home

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("courses/", include("courses.urls")),
    path("quiz/", include("assessments.urls")),
    path("attendance/", include("attendance.urls")),
    path("payments/", include("payments.urls")),
    path("live/", include("liveclasses.urls")),
    path("dashboard/", include("dashboard.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)