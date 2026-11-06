from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("meetings/", views.parent_meetings, name="parent_meetings"),
    path("meetings/request/", views.request_meeting, name="request_meeting"), 
    path("link-child/", views.link_child, name="link_child"),
    path("meetings/update/<int:meeting_id>/<str:status>/", views.update_meeting_status, name="update_meeting_status"),
    path("notifications/", views.notification_list, name="notification_list"),
    path("notifications/send/<int:course_id>/", views.send_teacher_notification, name="send_teacher_notification"),
    path("meetings/create/", views.create_meeting, name="create_meeting"),
]