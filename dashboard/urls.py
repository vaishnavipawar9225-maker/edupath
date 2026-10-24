from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("meetings/", views.parent_meetings, name="parent_meetings"),
    path("meetings/request/", views.request_meeting, name="request_meeting"), 
    path("link-child/", views.link_child, name="link_child"),
]