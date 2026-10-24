from django.urls import path
from . import views
urlpatterns = [
    path("", views.live_list, name="live_list"),
    path("<int:pk>/join/", views.join_class, name="join_class"),
]