

from django.contrib import admin
from .models import Attendance
from children.models import Children

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "child_id", "kindergarten_id", "date", "check_in_time", "check_out_time")
    search_fields = ("child__name", "child__id")  # Allow searching by child name or ID
    list_filter = ("date", "child__kindergarten")  # Filter by date or kindergarten

    def child_id(self, obj):
        return obj.child.id  # Show Child ID
    child_id.short_description = "Child ID"

    def kindergarten_id(self, obj):
        return obj.child.kindergarten.id if obj.child.kindergarten else None  # Show Kindergarten ID
    kindergarten_id.short_description = "Kindergarten ID"

admin.site.register(Attendance, AttendanceAdmin)