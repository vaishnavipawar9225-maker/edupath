from django.contrib import admin
from .models import LiveClass
@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "scheduled_at", "teacher", "jitsi_room")