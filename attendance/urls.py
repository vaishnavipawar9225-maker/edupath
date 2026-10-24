from django.urls import path
from . import views
urlpatterns = [
    path("mark/<int:course_id>/", views.mark_attendance, name="mark_attendance"),
    path("me/", views.my_attendance, name="my_attendance"),
]